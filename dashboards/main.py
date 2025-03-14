#################################################################################
#                                                                               #
#                       IDENTIFICATION DIVISION                                 #
#                                                                               #
#################################################################################
# This is the main program from the FJ Collector
# it receives inputs from a YAML configfile to collect metrics from
# different sources
#
# This is not a comercial product and it's 'as is' is basically for PoC that a 
# unique tool can get the most relevant data from a Datacenter and how easy
# it can be
#
# Also, will allow to the ones intervening in this process to acquire knowledge
# in different protocols and command lines to acquire the needed info

#################################################################################
#                                                                               #
#                       ENVIRONMENT DIVISION                                    #
#                                                                               #
#################################################################################
import sys, os, logging, time
from logging.handlers import RotatingFileHandler
from threading import Thread, Event
from functions_core.yaml_validate import *
from functions_core.gfun_main import *
from functions_core.utils import *
from functions import *


#################################################################################
#                                                                               #
#                       DATA DIVISION                                           #
#                                                                               #
#################################################################################

configfile = "config/config.yaml"
event = Event()

#################################################################################
#                                                                               #
#                       PROCEDURE DIVISION                                      #
#                                                                               #
#################################################################################


#################################################################################
#                                                                               #
#                       MAIN                                                    #
#                                                                               #
#################################################################################

if __name__ == "__main__":

    ########## BEGIN FUNCTIONS IN YAML_VALIDATE  ################################    
    config, orig_mtime, configfile_running = configfile_read(configfile)
    result_dicts, global_parms = create_metric_ip_dicts(config)
    ########## END FUNCTIONS IN YAML_VALIDATE  ##################################    


    ########## BEGIN - Start Logging Facility ###################################
    # Set up log rotation (10MB max file size and 5 backup files)
    log_file = global_parms['logfile']
    log_size = 10 * 1024 * 1024  # 10MB
    backup_count = 5
    #logging.basicConfig(filename=global_parms['logfile'], level=eval("logging."+global_parms['loglevel']), format='%(asctime)s %(levelname)s %(module)s %(threadName)s %(message)s', force=True)
    
    # Create a rotating file handler
    handler = RotatingFileHandler(log_file, maxBytes=log_size, backupCount=backup_count)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(module)s %(threadName)s %(message)s'))
    
    # Add the handler to the root logger
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(eval("logging." + global_parms['loglevel']))
    ########## END - Start Logging Facility #####################################    

    ########## BEGIN - Log configfile start processing ##########################
    logging.info("################ Starting Collector ################")
    ########## END - Log configfile start processing ############################
    
    logging.debug("Will print the dict that will be used: %s" % result_dicts)


    if config.global_parameters.auto_fungraph:
        #build_dashboards(config)
        gfun_main(config)
    

    while True:
        time.sleep(1)

        if orig_mtime < os.path.getmtime(configfile_running):
            logging.info("Configfile changed, will reload")

            event.set()
            
            orig_mtime = os.path.getmtime(configfile_running)
            config, orig_mtime, configfile_running = configfile_read(configfile)
            result_dicts, global_parms = create_metric_ip_dicts(config)


            logging.debug("Configfile changed, will reload with %s" % result_dicts)

            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)
                
            try:             
                #logging.basicConfig(filename=global_parms['logfile'], level=eval("logging."+global_parms['loglevel']), format='%(asctime)s %(levelname)s %(module)s %(threadName)s %(message)s', force=True)
                # Reconfigure logging with the updated config
                handler = RotatingFileHandler(log_file, maxBytes=log_size, backupCount=backup_count)
                handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(module)s %(threadName)s %(message)s'))
                logging.getLogger().addHandler(handler)
                logging.getLogger().setLevel(eval("logging." + global_parms['loglevel']))
            except Exception as msgerr:
                logging.fatal("Failed to change logging basicConfig %s" % msgerr)
                sys.exit()
            
            time.sleep(5)
            event.clear()
           
            if config.global_parameters.auto_fungraph:
                #build_dashboards(config)
                gfun_main(config)
            logging.info("Configfile reloaded")
            logging.debug("Configfile reloaded")