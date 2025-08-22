function openTab(evt, tabName, sizemultiplier=1) {
    // Declare all variables
    var i, tabcontent, tablinks;
  
    if (tabName !=="tempcodewindow"){
      tempcodewindow.setSize(null, 0);
      usetempcodewindow = false;
    }
    else{
      usetempcodewindow = true;
      tempcodewindow.setSize(null, 480*sizemultiplier);
    }
    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }
  
    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
  
    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(tabName).style.display = "block";
    document.getElementById(tabName).className += " active";
  }    
  //activate tab
