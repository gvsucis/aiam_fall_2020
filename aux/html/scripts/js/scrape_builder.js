const SCRAPE_BUILDER_PATH = '/aux/html/scripts/php/job_collector.php';
const SUBMIT_PROFILE_PATH = '/aux/html/scripts/php/submit_profile.php';

let scrapeHandler = async function ( data ) {
	// Expecting form data to be serialized as a javascript object
	// if using jquery simply pass in $('#some_example_form_id').serialize()
	// as the data parameter
 	let job_results = [];
	await $.ajax({
		type: "POST",
		url: SCRAPE_BUILDER_PATH,
		data: data,
		success: function ( response )
		{
			job_results = response.split('\n');
			return response.split('\n');
		}
	});
	console.log( job_results );
	return job_results;
}

let processNewScrapeProfile = async function ( companyName ) {
        let res = "Processing not finished, this is weird";
	await $.ajax({                                                           
		type: "POST",
		url: SUBMIT_PROFILE_PATH,
		data: {"company":companyName},
		success: function (response) {
			res = "Successfully processed submission!\n";
		},
		error: function (err) {
			res = "Something went wrong!\n";
		}
		
	});
	return res;
}
