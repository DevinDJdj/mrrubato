function addTagUI(tagvalue){
    const tags = document.getElementById('tags'); 
    const tag = document.createElement('li'); 
              
    // Get the trimmed value of the input element 
    const tagContent = tagvalue; 
  
    // If the trimmed value is not an empty string 
    if (tagContent !== '') { 
  
        // Set the text content of the tag to  
        // the trimmed value 
        tag.innerText = tagContent; 

        // Add a delete button to the tag 
        tag.innerHTML += '<button class="delete-button">X</button>'; 
          
        // Append the tag to the tags list 
        tags.appendChild(tag); 
          
        // Clear the input element's value 
        input.value = ''; 
    } 
} 

function removeTagUI(tagvalue){
    const tags = document.getElementById('tags'); 
    all = tags.childNodes;
    for (i=0; i<all.length; i++){
        if (all[i].innerText.substring(0, all[i].innerText.length-1) == tagvalue){
            tags.removeChild(all[i]);
        }
    }
}
        //each tag should be a word of some language.  
        // Get the tags and input elements from the DOM 
        const tags = document.getElementById('tags'); 
        const input = document.getElementById('input-tag'); 
  
        // Add an event listener for keydown on the input element 
        input.addEventListener('keydown', function (event) { 
  
            // Check if the key pressed is 'Enter' 
            if (event.key === 'Enter') { 
              
                // Prevent the default action of the keypress 
                // event (submitting the form) 
                event.preventDefault(); 
                
                addTag(input.value.trim());
            }
                // Create a new list item element for the tag 
        }); 

                // Add an event listener for click on the tags list 
                tags.addEventListener('click', function (event) { 
  
                    // If the clicked element has the class 'delete-button' 
                    if (event.target.classList.contains('delete-button')) { 
                      
                        // Remove the parent element (the tag) 
//                        event.target.parentNode.remove(); 
                        removeTag(event.target.parentNode.innerText.substring(0, event.target.parentNode.innerText.length-1));
                    } 
                }); 