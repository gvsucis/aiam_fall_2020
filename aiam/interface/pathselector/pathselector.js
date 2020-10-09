function updateClipboard(newClip) {
  navigator.clipboard.writeText(newClip)
  .then(function() {
  }, function() {
    console.log( "ERROR updating clipboard!" );
  });
}



function getPathTo( element, recursion ) {
	ret = ''

    //if (element.id!=='')
    //    ret = ret + 'id("' + element.id + '")';
   if (element===document.body || recursion >= 2 )
        ret = element.tagName.toLowerCase()
   	else 
   	{
   		var ix= 0;
	    var siblings= element.parentNode.childNodes;
	    for (var i= 0; i<siblings.length; i++) {
	        var sibling= siblings[i];
	        if (sibling===element) {

	        	let classData = element.className
	        	// parse all classes for an element
	        	if ( classData.length > 0)
	        	{
	        		let classes = classData.split(" ");
	        		// some elements have more than 1 class, need to parse all
	        		classData = '[contains(@class, "' + classes[0] + '")]'	
	        		
	        	}

	        	let index = ''
	        	console.log(element.tagName);
	        	if ( element.tagName === 'TD' )
	        	{
	        		index = '['+(ix+1)+']'
	        	}

	        	//if ( siblings.length <= 1 )
	        	//{
	        	//	index = ''
	        	//}
	        	

	            ret = ret + getPathTo(element.parentNode, recursion+1)+'/'+ element.tagName.toLowerCase() + classData + index;
	        }
	        if (sibling.nodeType===1 && sibling.tagName===element.tagName)
	            ix++;
	    }
   	}

   	return '//' + ret.replaceAll( '//', '');
}

/*
const getPathTo = (element, isParent) => {
	let ret = "//" + element.tagName.toLowerCase()

	if ( !isParent || element.className.length <= 0)
	{
		ret = getPathTo(element.parentElement, true) + '/' + element.tagName.toLowerCase();
	}
	
	if ( element.className.length > 0 ) {
		const classData = 
		ret += classData;
	}

	if ( !isParent )
	{
		let parent = element.parentElement;
		for ( let i=0; i < parent.children.length; ++i )
		{
			if ( parent.children[i] == element )
			{
				ret += '[' + (i+1) + ']'
			}
		}
	}

	return ret;
}
*/

const getLeafNodes = ( rootNode ) => {
	const listArray = Array.from( rootNode.children );

	listArray.forEach( ( item ) => {
		if ( item.children.length < 1 )
		{
			try {

				if ( item.getAttribute('href') != null)
				{
					item.setAttribute('link',item.getAttribute('href'));
					item.setAttribute('href', 'javascript: void(0);');
				}

				/*if ( item.style.display == "none" )
				{
					console.log("QQQQQQQQQQQQQ");
					item = item.parentElement;
				}*/			
				console.log(item);	
				item.addEventListener( "click", () => {
					let newPath = getPathTo( item, 0 );
					updateClipboard( newPath );
				} )

			}
			catch (e) {
				console.log("ERR " + e);
			}
		}
		else
		{
			return getLeafNodes( item );
		}
		
	});
}

const run = () => {
	console.log("RUNNNING");

	const roots = Array.from( document.body.children );
	roots.forEach( ( root) => { getLeafNodes( root ); } );

	console.log("DONE");
}

console.log("XXXX");

run();