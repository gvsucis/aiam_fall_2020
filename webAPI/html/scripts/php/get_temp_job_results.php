<?php

	include 'env/env.php';
	$RESULTS_DIR = env_get( "RESULTS_DIR" );
	$PYTHON_VENV_PATH = env_get( "PYTHON_VENV_PATH" );
	$SCRAPE_ENGINE_ROOT_DIR = env_get( "SCRAPE_ENGINE_ROOT_DIR" );

	$company = $_GET[ 'company' ];
	$temp_results_file = $RESULTS_DIR . $company . '-jobs.txt'; 
	
	$results = file_get_contents( $temp_results_file );
		
	echo $results;
?>
