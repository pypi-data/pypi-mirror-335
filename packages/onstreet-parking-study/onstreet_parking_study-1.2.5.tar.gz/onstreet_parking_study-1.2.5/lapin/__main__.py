"""Lapin analysis

This script allows the user to perform a parking analysis by using LAPI
data.

This framework accepts config files as specified in config.py.

The framework requires that several dependencies be installed within the Python
environment you are running this script in. Those are specified in the
requirements.txt

This file can also be imported as a module and contains the following
functions:

    * aggregate_one_way_street - aggregate lectures of both side for
    one way street
    * main - the main function of the script

"""

import json
import os
import sys
import time
import argparse
from pathlib import Path
import logging.config
import logging
from datetime import datetime
from typing import cast

import pandas as pd
import geopandas as gpd
import osmnx as ox
import typer

from lapin.processing import enhance, remove_noizy_readings
from lapin.processing.filter import remove_veh_parked_on_restrictions
from lapin.io.load import data_from_conf
from lapin.tools.graph import convert_geobase_to_osmnx
from lapin.tools.curbsnapp import get_project_capacities

from lapin import constants
from lapin.scheduler import Scheduler
from lapin.core import (
    TrajDataFrame,
    LprDataFrame,
    RoadNetwork,
    RoadNetworkDouble,
    Curbs,
)
from lapin.scheduler import SchedulerDataStore

from lapin.configs import user_conf, others

LOGGING_CONFIG = Path(__file__).parent / "logging.conf"
logging.config.fileConfig(LOGGING_CONFIG)
logger = logging.getLogger("lapin")


app = typer.Typer()

conf_path: str = typer.Argument(
    ...,
    help="Path of the configuration file for the analysis or the json value as string",
)
from_dt: list[datetime] = typer.Argument(
    ..., help="Dates to process, this are the from dates."
)
to_dt: list[datetime] = typer.Argument(
    ..., help="Dates to process, this are the to dates"
)
# dates: list[dict[str, datetime]] = typer.Argument(
#     ...,
#     help="Dates to process for the analysis or preprocessing. Must be in the "
#     + "following format [ { 'from': 'YYYY-MM-DD', 'to': 'YYYY-MM-DD'  }, ... ]. "
#     + "Dates are in local, i.e. America/Montreal.",
# )


def get_data(conf: user_conf.UserConfig) -> SchedulerDataStore:
    """_summary_

    Parameters
    ----------
    conf : config.UserConfig
        _description_

    Returns
    -------
    Analysis data
        All external data for analysis
    """
    logger.info("loading datasets.")

    # TODO: Handle when there is no preprocessed data for a geobase_version but there is raw data
    logger.debug("reading lpr_dataset")
    logger.debug(user_conf.LPR_CONNECTION)
    lpr_data = LprDataFrame.from_postgres(**user_conf.LPR_CONNECTION)
    logger.debug("reading veh_dataset")
    logger.debug(user_conf.VEH_CONNECTION)
    veh_data = TrajDataFrame.from_postgres(**user_conf.VEH_CONNECTION)

    logger.debug("reading road networks")
    roads = RoadNetwork.load_geobase_from_curbsnap(conf.curbsnapp_projects_id)
    geodbl = RoadNetworkDouble.load_geobase_from_curbsnap(conf.curbsnapp_projects_id)

    logger.debug("reading delims")

    regs = data_from_conf(others.DISCRETISATION_CONNECTION)
    regs = cast(gpd.GeoDataFrame, regs)

    analysis_data = SchedulerDataStore(
        lpr_data=lpr_data,
        veh_data=veh_data,
        roads=roads,
        roadsdb=geodbl,
        restriction_handler=Curbs({}),
        trips=None,
        grid_trips_origin=regs,
    )

    return analysis_data


@app.command()
def extract_data_cosmos(
    from_dt: list[datetime] = from_dt, to_dt: list[datetime] = to_dt
):

    # get configuration for cosmos connections
    lpr_conf = copy.deepcopy(user_conf.LPR_CONNECTION)
    veh_conf = copy.deepcopy(user_conf.VEH_CONNECTION)

    # extract data from cosmos
    lpr_data = LprDataFrame.from_azure_cosmos(**user_conf.LPR_CONNECTION)
    logger.debug("reading veh_dataset")
    veh_data = TrajDataFrame.from_azure_cosmos(**user_conf.VEH_CONNECTION)
    logger.debug("reading road networks")

    # populate the warehouse
    # lpr_data.to_sql()


@app.command()
def launch_preprocessing(
    geobase_version: int,
    from_dt: list[datetime] = from_dt,
    to_dt: list[datetime] = to_dt,
):

    # Extract
    logger.info("loading datasets.")
    logger.debug("reading lpr_dataset")
    lpr_data = LprDataFrame.from_azure_cosmos(**user_conf.LPR_CONNECTION)
    logger.debug("reading veh_dataset")
    veh_data = TrajDataFrame.from_azure_cosmos(**user_conf.VEH_CONNECTION)
    logger.debug("reading road networks")

    roads = RoadNetwork.load_geobase_from_curbsnap(conf.curbsnapp_projects_id)
    geodbl = RoadNetworkDouble.load_geobase_from_curbsnap(conf.curbsnapp_projects_id)

    # Transform
    logger.info("preprocessing starts.")

    logger.info("computing enhancement")
    lpr_data, veh_data, trips, _ = enhance(
        lpr_data=lpr_data,
        veh_data=veh_data,
        roads=roads,
        geodouble=geodbl,
        matcher_host="http://localhost:8002",
        matcher_client="valhalla",
        prov_conf=user_conf.PROV_CONF,
    )
    logger.info("enhancement finished")

    # Load
    # save_lpr_data
    # save_veh_data


@app.command()
def launch_study(
    conf_file: str = conf_path,
    run_id: int = -1,
    conf_id: int = -1,
    from_dict: bool = False,
    debug: bool = False,
    to_db: bool = False,
):
    """Launch a LAPI analysis having configuration defined by the config file

    Parameters
    ----------
    conf_file : Path
        Path of the configuration file to use for the analysis.
    run_id : int, optional
        Optional ID for this analysis. It is used when results are saved into a
        database along multiple other runs.
    """

    if debug:
        logger.setLevel(logging.DEBUG)

    logger.info("Analysis starting")
    # Retrieve conf
    conf = load_config_file(conf_file, from_dict)
    cache_path = os.path.join(conf.work_folder, "cache")

    logger.info("treating project : %s", conf.title_proj)
    logger.info("run id : %s, conf id : %s", run_id, conf_id)

    # read_data
    analysis_data = get_data(conf)

    if analysis_data.lpr_data.empty or analysis_data.veh_data.empty:
        logger.error("no data. Quitting.")
        sys.exit(2)

    # restriction handler
    analysis_data.restriction_handler = load_regulation(
        project_ids=conf.curbsnapp_projects_id,
        roads=analysis_data.roads,
        cache_path=cache_path,
        restrictions_ignore=conf.restrictions_to_exclude,
        veh_size=conf.veh_size,
    )

    # Compute capacity and restriction for each plate
    analysis_data.lpr_data = apply_restrictions(
        analysis_data.lpr_data,
        analysis_data.restriction_handler,
        cache_path,
        conf.allow_veh_on_restrictions,
    )

    if conf.handle_restriction:
        analysis_data.lpr_data = remove_veh_parked_on_restrictions(
            analysis_data.lpr_data
        )

    scheduler = Scheduler.from_datas(
        conf=conf, analysis_data=analysis_data, run_id=run_id, conf_id=conf_id
    )
    scheduler.db_load = to_db

    scheduler.launch()


@app.command()
def generate_graph(output: Path = Path(constants.VALHALLA_DFLT_FOLDER)):
    """Create and save a osm.pbf graph version of Montreal Geobase."""
    logger.info("Generating OSM graph from Montreal's geobase")
    # extract geobase
    geobase = RoadNetwork.load_geobase_from_mtl_open_data()

    # constrcut graph from geobase
    ox.settings.all_oneway = True
    G_osm = convert_geobase_to_osmnx(geobase, traffic_dir=True)

    # save geobase to file_system
    os.makedirs(output, exist_ok=True)
    ox.save_graph_xml(
        G_osm,
        os.path.abspath(os.path.join(output, "..", "graph_geobase_osm.osm")),
    )

    # convert graph to pbf
    os.system(
        "osmium.exe cat "
        + os.path.abspath(os.path.join(output, "..", "graph_geobase_osm.osm"))
        + " -f pbf -o "
        + os.path.abspath(os.path.join(output, "..", "graph_geobase.osm.pbf"))
        + " --overwrite"
    )
    os.system(
        "osmium.exe sort "
        + os.path.abspath(os.path.join(output, "..", "graph_geobase.osm.pbf"))
        + " -o "
        + os.path.abspath(os.path.join(output, "..", "graph_geobase_sorted.osm.pbf"))
        + " --overwrite"
    )

    # put it in the valhalla folder
    os.system(
        "move/y "
        + os.path.abspath(
            os.path.join(output.as_posix(), "..", "graph_geobase_sorted.osm.pbf")
        )
        + " "
        + output
    )
    logger.info("If using with valhalla, " + "please construct the graph before.")
    logger.info("You can use the following command : ")
    logger.info(
        "\tsudo docker run --rm --name valhalla_gis-ops "
        + "-p 8002:8002 -v $PWD/data/network/valhalla:/custom_files "
        + "-e tile ghcr.io/gis-ops/docker-valhalla/valhalla:latest"
    )
    logger.info("Otherwise, see OSRM doc to construct " + "the graph with this file.")


def load_config_file(config: str, from_dict: bool = False) -> user_conf.UserConfig:
    """Try to open configuration file at path

    Parameters
    ----------
    conf_path : str
        Path to the config file

    Returns
    -------
    UserConfig
    """
    try:
        if not from_dict:
            conf = user_conf.UserConfig.from_file(config)
        else:
            config_f = json.loads(config)
            conf = user_conf.UserConfig.from_dict(config_f)
    except Exception as e:
        logger.error("please provide a valid conf file.")
        logger.error(e)
        sys.exit(1)

    return conf


def retrive_data(conf: user_conf.UserConfig) -> SchedulerDataStore:
    """_summary_

    Parameters
    ----------
    conf : config.UserConfig
        _description_

    Returns
    -------
    Analysis data
        All external data for analysis
    """
    lpr_data = pd.DataFrame()
    veh_data = pd.DataFrame()
    logger.info("loading datasets.")

    logger.debug("reading lpr_dataset")
    # if not os.path.exists(conf.work_folder + "/cache/lpr_data_enhanced.csv"):
    lpr_data = LprDataFrame.from_azure_cosmos(**user_conf.LPR_CONNECTION)
    # else:
    #     lpr_data.insert(0, "dummy", [-1])
    logger.debug("reading veh_dataset")
    # if not os.path.exists(conf.work_folder + "/cache/veh_data_enhanced.csv"):
    veh_data = TrajDataFrame.from_azure_cosmos(**user_conf.VEH_CONNECTION)
    # else:
    #     veh_data.insert(0, "dummy", [-1])
    logger.debug("reading road networks")
    roads = RoadNetwork.load_geobase_from_curbsnap(conf.curbsnapp_projects_id)
    geodbl = RoadNetworkDouble.load_geobase_from_curbsnap(conf.curbsnapp_projects_id)

    logger.debug("reading delims")
    delim = data_from_conf(user_conf.DELIM_CONNECTION)
    vis_delim = data_from_conf(user_conf.VIS_DELIM_CONNECTION)

    regs = data_from_conf(others.DISCRETISATION_CONNECTION)

    analysis_data = SchedulerDataStore(
        lpr_data=lpr_data,
        veh_data=veh_data,
        roads=roads,
        roadsdb=geodbl,
        restriction_handler=None,
        trips=None,
        grid_trips_origin=regs,
        delim=delim,
        vis_delim=vis_delim,
    )

    return analysis_data


def load_regulation(
    project_ids: list[str],
    roads: RoadNetwork,
    cache_path: str,
    restrictions_ignore: list[str] = constants.IGNORE_FOR_CAPACITY,
    veh_size: float = constants.VEH_SIZE,
) -> Curbs:
    """_summary_

    Parameters
    ----------
    conf : config.UserConfig
        _description_
    roads : RoadNetwork
        _description_

    Returns
    -------
    Curbs
        _description_
    """
    logger.info("querying regulations from curbsnapp")
    json_regulation = get_project_capacities(project_ids)
    # Apply restriction
    if restrictions_ignore and "Défaut" in restrictions_ignore:
        restrictions_ignore = constants.IGNORE_FOR_CAPACITY

    logger.info("extracting curb regulation from curbsnapp")

    try:
        curbs_cache = pd.read_csv(
            os.path.join(cache_path, "curbs_cache.csv"),
            parse_dates=["start_time", "end_time", "start_date", "end_date"],
        )
        restriction_handler = Curbs.from_dataframe(
            data=curbs_cache, veh_size=veh_size, regulation_ignored=restrictions_ignore
        )
    except FileNotFoundError:
        restriction_handler = Curbs.from_json(
            regulations=json_regulation,
            roads=roads,
            veh_size=veh_size,
            regulation_ignored=restrictions_ignore,
        )
        restriction_handler.to_dataframe().to_csv(
            os.path.join(cache_path, "curbs_cache.csv"),
            index=False,
        )

    return restriction_handler


def preprocessing(lpr_data, veh_data, roads, geodbl, cache_path):
    """_summary_

    Parameters
    ----------
    lpr_data : _type_
        _description_
    veh_data : _type_
        _description_
    roads : _type_
        _description_
    geodbl : _type_
        _description_
    work_folder : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    logger.info("preprocessing starts.")

    logger.info("computing enhancement")
    lpr_data, veh_data, trips, _ = enhance(
        lpr_data=lpr_data,
        veh_data=veh_data,
        roads=roads,
        geodouble=geodbl,
        save_path=cache_path,
        matcher_host="http://localhost:8002",
        matcher_client="valhalla",
        prov_conf=user_conf.PROV_CONF,
    )
    logger.info("enhancement finished")

    return lpr_data, veh_data, trips


def apply_restrictions(
    lpr_data: LprDataFrame,
    restriction_handler: Curbs,
    save_path: str,
    allow_veh_on_restrictions: list[str] | None = None,
) -> LprDataFrame:
    """_summary_

    Parameters
    ----------
    lpr_data : LprDataFrame
        _description_
    restriction_handler : Curbs
        _description_
    save_path : str
        _description_
    allow_veh_on_restrictions : bool, optional
        _description_, by default False

    Returns
    -------
    LprDataFrame
        _description_
    """
    t0 = time.time()
    lpr_data[constants.DATETIME] = pd.to_datetime(lpr_data[constants.DATETIME])
    lpr_data = restriction_handler.apply_restriction_on_lprdataframe(
        lpr_df=lpr_data, return_capacity=True, ignore_reg=allow_veh_on_restrictions
    )
    t1 = time.time()
    # save them
    lpr_data.to_csv(
        os.path.join(save_path, "lpr_data_enhanced_restrict.csv"), index=False
    )
    logger.info("regulation process executed in %s seconds", t1 - t0)
    logger.info("regulation computation finished")

    return lpr_data


def analysis(conf_path):
    """
    Excecute all of the analysis for the config file conf_path
    """
    logger.info("analysis starting")

    # Retrieve conf
    conf = load_config_file(conf_path)
    cache_path = os.path.join(conf.work_folder, "cache")

    logger.info("treating project : %s", conf.title_proj)

    # read_data
    analysis_data = retrive_data(conf)

    if analysis_data.lpr_data.empty or analysis_data.veh_data.empty:
        logger.error("no data. Quitting.")
        sys.exit(2)

    # preprocessing
    lpr_data, veh_data, trips = preprocessing(
        analysis_data.lpr_data,
        analysis_data.veh_data,
        analysis_data.roads,
        analysis_data.roadsdb,
        cache_path,
    )

    analysis_data.lpr_data = lpr_data
    analysis_data.veh_data = veh_data
    analysis_data.trips = trips

    # restriction handler
    analysis_data.restriction_handler = load_regulation(
        project_ids=conf.curbsnapp_projects_id,
        roads=analysis_data.roads,
        cache_path=cache_path,
        restrictions_ignore=conf.restrictions_to_exclude,
        veh_size=conf.veh_size,
    )

    # Compute capacity and restriction for each plate
    analysis_data.lpr_data = apply_restrictions(
        analysis_data.lpr_data,
        analysis_data.restriction_handler,
        cache_path,
        conf.allow_veh_on_restrictions,
    )

    if conf.handle_restriction:
        analysis_data.lpr_data = remove_veh_parked_on_restrictions(
            analysis_data.lpr_data
        )

    # remove noizy readings (needs to be done after restriction)
    analysis_data.lpr_data = remove_noizy_readings(
        data=analysis_data.lpr_data,
        roads=analysis_data.roads,
        threshold=2,
        roads_id_col=constants.SEGMENT,
    )

    scheduler = Scheduler.from_datas(
        conf=conf,
        analysis_data=analysis_data,
    )

    scheduler.launch()


def parse_args():
    """Argument parser when module is launch.

    Returns
    -------
    argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description="This program compute parking occupancy "
        + "analysis based on LAPI aquiered data."
    )

    parser.add_argument(
        "--conf-file",
        dest="conf_file",
        type=str,
        default=None,
        help="Project configuration file for the analysis.",
    )
    parser.add_argument(
        "-c",
        "--generate-conf-file",
        dest="generate_conf_file",
        default=False,
        action="store_true",
        help="Generate a blank configuration file without executing",
    )
    parser.add_argument(
        "-G",
        "--generate-graph",
        dest="generate_graph",
        default=False,
        action="store_true",
        help="Generate the osrm graph from the geobase",
    )
    parser.add_argument(
        "-p",
        "--preprocessing-only",
        dest="preprocessing_only",
        default=False,
        action="store_true",
        help="Only does the preprocessing steps",
    )

    # Read arguments from command line
    return parser.parse_args()


if __name__ == "__main__":

    app()
    # Logging
    # args = parse_args()

    # if args.generate_conf_file:
    #     try:
    #         os.remove("./config_files/blank_conf_file.config")
    #     except FileNotFoundError:
    #         pass
    #     finally:
    #         user_conf.UserConfig(
    #             "./config_files/blank_conf_file.config", encoding="utf-8"
    #         )
    #         sys.exit(1)

    # if args.generate_graph:
    #     logger.info("Generating OSM graph from Montreal's geobase")
    #     geobase = RoadNetwork.load_geobase_from_mtl_open_data()
    #     ox.settings.all_oneway = True
    #     G_osm = convert_geobase_to_osmnx(geobase, traffic_dir=True)
    #     os.makedirs(constants.VALHALLA_DFLT_FOLDER, exist_ok=True)
    #     ox.save_graph_xml(
    #         G_osm,
    #         os.path.abspath(
    #             os.path.join(
    #                 constants.VALHALLA_DFLT_FOLDER, "..", "graph_geobase_osm.osm"
    #             )
    #         ),
    #     )
    #     os.system(
    #         "osmium.exe cat "
    #         + os.path.abspath(
    #             os.path.join(
    #                 constants.VALHALLA_DFLT_FOLDER, "..", "graph_geobase_osm.osm"
    #             )
    #         )
    #         + " -f pbf -o "
    #         + os.path.abspath(
    #             os.path.join(
    #                 constants.VALHALLA_DFLT_FOLDER, "..", "graph_geobase.osm.pbf"
    #             )
    #         )
    #         + " --overwrite"
    #     )
    #     os.system(
    #         "osmium.exe sort "
    #         + os.path.abspath(
    #             os.path.join(
    #                 constants.VALHALLA_DFLT_FOLDER, "..", "graph_geobase.osm.pbf"
    #             )
    #         )
    #         + " -o "
    #         + os.path.abspath(
    #             os.path.join(
    #                 constants.VALHALLA_DFLT_FOLDER, "..", "graph_geobase_sorted.osm.pbf"
    #             )
    #         )
    #         + " --overwrite"
    #     )
    #     os.system(
    #         "move/y "
    #         + os.path.abspath(
    #             os.path.join(
    #                 constants.VALHALLA_DFLT_FOLDER, "..", "graph_geobase_sorted.osm.pbf"
    #             )
    #         )
    #         + " "
    #         + constants.VALHALLA_DFLT_FOLDER
    #     )
    #     logger.info("If using with valhalla, " + "please construct the graph before.")
    #     logger.info("You can use the following command : ")
    #     logger.info(
    #         "\tsudo docker run --rm --name valhalla_gis-ops "
    #         + "-p 8002:8002 -v $PWD/data/network/valhalla:/custom_files "
    #         + "-e tile ghcr.io/gis-ops/docker-valhalla/valhalla:latest"
    #     )
    #     logger.info(
    #         "Otherwise, see OSRM doc to construct " + "the graph with this file."
    #     )
    #     sys.exit(1)

    # # Select a config file from Tk window
    # if not args.conf_file:
    #     Tk().withdraw()
    #     config_file = askopenfilename(
    #         filetypes=[("Configuration files", "*.config")],
    #         initialdir=os.path.join(os.getcwd(), "../config_files"),
    #         title="Select files",
    #         multiple=False,
    #     )
    # else:
    #     config_file = args.conf_file

    # if args.preprocessing_only:
    #     conf = load_config_file(config_file)
    #     datastore = retrive_data(conf)
    #     _ = preprocessing(
    #         lpr_data=datastore.lpr_data,
    #         veh_data=datastore.veh_data,
    #         roads=datastore.roads,
    #         geodbl=datastore.roadsbl,
    #         cache_path=conf.work_folder + "/cache",
    #     )
    #     sys.exit(0)

    # # Execute main analysis
    # analysis(config_file)
