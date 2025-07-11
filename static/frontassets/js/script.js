function showSearch(sicon){
const mobsearch=sicon.nextElementSibling;
mobsearch.style.display='none';

};

function show(button) {
    const showBox = button.querySelector('.show-box');
    
    // Toggle visibility
    if (showBox.style.display === 'none') {
      showBox.style.display = 'block';
      
      // Add click listener to close when clicking outside
      setTimeout(() => {
        document.addEventListener('click', function outsideClick(e) {
          if (!button.contains(e.target) ) {
            showBox.style.display = 'none';
            document.removeEventListener('click', outsideClick);
          }
        });
      }, 0);
      
    } else {
      showBox.style.display = 'none';
    }
    
   
  }