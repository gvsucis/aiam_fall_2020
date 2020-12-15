const SCRAPE_BUILDER_PATH = '/aux/html/scripts/php/job_collector.php';
const GET_TEMP_COMPANIES_PATH = '/aux/html/scripts/php/get_temp_profiles.php';
const DELETE_TEMP_PROFILE_PATH = '/aux/html/scripts/php/delete_temp_profile.php';
const GET_ACTIVE_COMPANIES_PATH = '/aux/html/scripts/php/get_active_profiles.php';
const DELETE_ACTIVE_PROFILE_PATH = '/aux/html/scripts/php/delete_active_profile.php';
const ACTIVATE_PROFILE_PATH = '/aux/html/scripts/php/activate_profile.php';
const RUN_TEMP_PATH = '/aux/html/scripts/php/test_temp_profile.php';
const RUN_ACTIVE_PATH = '/aux/html/scripts/php/test_active_profile.php';
const GET_TEMP_JOB_RESULTS_PATH = '/aux/html/scripts/php/get_temp_job_results.php';
const GET_ACTIVE_JOB_RESULTS_PATH = '/aux/html/scripts/php/get_active_job_results.php';
const RUN_ALL_ACTIVE_PROFILES_PATH = '/aux/html/scripts/php/run_all_active_profiles.php';

let getActiveCompanies = async function () {
	        companies = {};
	        await $.ajax({
			type: "GET",
			url: GET_ACTIVE_COMPANIES_PATH,
			success: function ( response )
			{
				companies = JSON.parse( response );
				return JSON.parse( response );
			}
		});
	        return companies;
}

let deleteActiveCompany = async function ( companyName ) {                                                                                                                                                                                             let ret = "Something went wrong during deletion!";                                                                                                                                                                                           await $.ajax({                                                                                                                                                                                                                                       type: "POST",                                                                                                                                                                                                                                url: DELETE_ACTIVE_PROFILE_PATH,                                                                                                                                                                                                               data: { "company": companyName },                                                                                                                                                                                                            success: function ( response ) {                                                                                                                                                                                                                          ret = "Success";                                                                                                                                                                                                                     },                                                                                                                                                                                                                                           error: function ( err ) {                                                                                                                                                                                                                            ret = "Error deleting profile";                                                                                                                                                                                                      }                                                                                                                                                                                                                                    });                                                                                                                                                                                                                                          return ret;                                                                                                                                                                                                                        } 

let scrapeActiveCompany = async function ( companyName ) {
	        await $.ajax( {
			                type: "POST",
			                url: RUN_ACTIVE_PATH,
			                data: { "company": companyName },
			                success: function ( response ) {
						                        return { "Success": response };//return JSON.parse( response );
						                },
			                error: function ( err ) {
						                        return { "Error": err };
						                }
			        } );
	        return;
}

const getJobsForActiveCompany = async function ( companyName ) {
	let active_job_results = {};
	await $.ajax({
		type:"GET",
		url: GET_ACTIVE_JOB_RESULTS_PATH,
		data: { "company": companyName },
                success: function ( response ) {
			                        active_job_results = JSON.parse( response );
			                },
		                error: function ( err ) {
					active_job_results = { 'error': err };
		                }
	})
	return active_job_results;
}

let getTempCompanies = async function () {
	let temp_companies = {};
	await $.ajax({
		type: "GET",
		url: GET_TEMP_COMPANIES_PATH,
		success: function ( response )
		{
			temp_companies = JSON.parse( response );
			console.log( temp_companies );
			return JSON.parse( response );
		}
	});
	return temp_companies;
}

let deleteTempCompany = async function ( companyName ) {
	let ret = "Something went wrong during deletion!";
	await $.ajax({
                type: "POST",
		url: DELETE_TEMP_PROFILE_PATH,
		data: { "company": companyName },
		success: function ( response ) {
			ret = "Success";
		},
		error: function ( err ) {
			ret = "Error deleting profile";
		}
	});
	return ret;
}

let scrapeTempCompany = async function ( companyName ) {
	await $.ajax( {
		type: "POST",
		url: RUN_TEMP_PATH,
		data: { "company": companyName },
		success: function ( response ) {
			return { "Success": response };//return JSON.parse( response );
		},
		error: function ( err ) {
			return { "Error": err };
		}
	} );
	return;
}

let getJobsForTempCompany = async function ( companyName ) {
	let temp_job_results = [];
	await $.ajax ( {
		type: "GET",
		url: GET_TEMP_JOB_RESULTS_PATH,
		data: { "company": companyName },
		success: function ( response ) {
			temp_job_results = response.split( '\n' );
		},
		error: function ( err ) {
			temp_job_results = [ 'error' ];
		}
	} );
	return temp_job_results;
}

let runAllActiveProfiles = async function () {
	let ret = "Running";
	await $.ajax ( {
		type: "GET",
		url: RUN_ALL_ACTIVE_PROFILES_PATH,
		data: {},
		success: function ( response ) {
			ret = "Done";
		},
		error: function ( err ) {
			ret = err
		}
	} );
	return "Done";
}
let testingStuff = function () {
	console.log("hewwo");
}
const activateProfile = async function ( companyName ) {
	let ret = "Something went wrong!";
	await $.ajax({
		type: "POST",
		url: ACTIVATE_PROFILE_PATH,
		data: { "company": companyName },
		success: function ( response ) {
			ret = "Success";
		},
		error: function ( err ) {
			ret = "Error activating profile";
		}
	})
	return ret;
}
