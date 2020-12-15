<?php
	include 'env/env.php';
	$PYTHON_VENV_PATH = env_get( "PYTHON_VENV_PATH" );
	$SCRAPE_ENGINE_ROOT_DIR = env_get( "SCRAPE_ENGINE_ROOT_DIR" );

	$company = $_GET[ 'company' ];

	$command_template = "cd %s; %s -c \"from Models import getJobsForActiveCompany; getJobsForActiveCompany( '%s' )\"";
	$exec = sprintf( $command_template, $SCRAPE_ENGINE_ROOT_DIR, $PYTHON_VENV_PATH, $company );  

	$profiles = shell_exec( $exec );	
	echo $profiles;
?>
