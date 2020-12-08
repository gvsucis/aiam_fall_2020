<?php
	include 'env/env.php';
	$BUILD_PARAMS_DIR = env_get( "BUILD_PARAMS_DIR" );
        $PYTHON_VENV_PATH = env_get( "PYTHON_VENV_PATH" );
	$SCRAPE_ENGINE_ROOT_DIR = env_get( "SCRAPE_ENGINE_ROOT_DIR" );
	
	$target = $BUILD_PARAMS_DIR . str_replace( ' ', '_', 'JR' ) . '_params.json';

	$command_template = "cd %s; %s -c \"from Models import addTempCompany; addTempCompany('%s')\"";
	$exec = sprintf( $command_template, $SCRAPE_ENGINE_ROOT_DIR, $PYTHON_VENV_PATH, $target );
	echo $exec;
	shell_exec( $exec );

	echo "success!\n";
?>
