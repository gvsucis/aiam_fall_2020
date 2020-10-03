function updateClipboard(newClip) {
  navigator.clipboard.writeText(newClip)
  .then(function() {
  }, function() {
    console.log( "ERROR updating clipboard!" );
  });
}


function getPathTo(element) {
	ret = ''

    //if (element.id!=='')
    //    ret = ret + 'id("' + element.id + '")';
   if (element===document.body)
        ret = ret + element.tagName;
   	else 
   	{
   		var ix= 0;
	    var siblings= element.parentNode.childNodes;
	    for (var i= 0; i<siblings.length; i++) {
	        var sibling= siblings[i];
	        if (sibling===element) {
	            ret = ret + getPathTo(element.parentNode)+'/'+ element.tagName +'['+(ix+1)+']';
	        }
	        if (sibling.nodeType===1 && sibling.tagName===element.tagName)
	            ix++;
	    }
   	}

   	return '/html/' + ret.replaceAll( '/html/', '').replaceAll( '[1]', '' ).toLowerCase();
}

const getLeafNodes = ( rootNode ) => {
	const listArray = Array.from( rootNode.children );

	listArray.forEach( ( item ) => {
		if ( item.children.length < 1 )
		{
			try {
				item.addEventListener( "click", () => {
					console.log("A");
					let newPath = getPathTo( item );
					console.log( newPath );
					updateClipboard( newPath );
				} )
			}
			catch (e) {
				console.log("ERR " + e);
			}
		}
		else
		{
			getLeafNodes( item );
		}
		
	});
}

const run = () => {
	console.log("RUNNNING");

	const roots = Array.from( document.body.children );
	roots.forEach( ( root) => { getLeafNodes( root ); } );

	console.log("DONE");
}

run();