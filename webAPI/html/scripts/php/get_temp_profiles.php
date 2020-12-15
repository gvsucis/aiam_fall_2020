<?php
	include 'env/env.php';
        $PYTHON_VENV_PATH = env_get( "PYTHON_VENV_PATH" );
        $SCRAPE_ENGINE_ROOT_DIR = env_get( "SCRAPE_ENGINE_ROOT_DIR" );

	$command_template = "cd %s; %s -c \"from Models import getTempCompanies; getTempCompanies()\"";
	$exec = sprintf( $command_template, $SCRAPE_ENGINE_ROOT_DIR, $PYTHON_VENV_PATH );

	$profiles = shell_exec( $exec );

	echo $profiles;
?>
