<?php
	include 'env/env.php';
        $PYTHON_VENV_PATH = env_get( "PYTHON_VENV_PATH" );
        $SCRAPE_ENGINE_ROOT_DIR = env_get( "SCRAPE_ENGINE_ROOT_DIR" );

	$company = $_POST[ 'company' ];

	$command_template = "cd %s; %s -c \"from Models import deleteActiveCompany; deleteActiveCompany('%s')\"";
	$exec = sprintf( $command_template, $SCRAPE_ENGINE_ROOT_DIR, $PYTHON_VENV_PATH, $company );

	echo shell_exec( $exec );
?>
