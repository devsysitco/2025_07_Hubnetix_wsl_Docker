const menuClose=document.querySelector('.menu-close');
const sideBar=document.querySelector('.dash-sidebar');
const menuOpen=document.querySelector('.sideopen');


menuClose.addEventListener('click', ()=>{
sideBar.style.left='-250px';
})

menuOpen.addEventListener('click', ()=>{
    sideBar.style.left='0';
})





$( function() {
    $( ".datepicker" ).datepicker({
      showOn: "button",
      buttonImage: "assets/media/cal-ico.svg",
      buttonImageOnly: true,
      buttonText: "Select date",
      changeMonth: true, // Allows the month to be changed via a dropdown
        changeYear: true, // Allows the year to be changed via a dropdown
      dateFormat: "dd/mm/yy", // Specify the date format here
      yearRange: "c-100:c+10"
    });
  } );