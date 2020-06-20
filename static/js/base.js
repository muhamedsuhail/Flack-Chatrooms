var user=document.querySelector("#us").innerHTML
var menu=document.querySelector('#mylinks');
var menuicon=document.querySelector('.icon');
var logout=document.querySelector('#logout');
var click_event=(/iPhone|iPad|iPod|Android/i.test(navigator.userAgent))? 'touchstart':'click';

if(click_event=='click')
{
  alert("The layout of this website is designed for mobile. For better experience visit the website in your mobile browser")
}

//Stores user to localStorage for retrieval of previous session.

localStorage.setItem("last_user",user);

menuicon.addEventListener(click_event,
function event()
{
    menu.style.display=(menu.style.display== "none" || menu.style.display== "" ) ?  "block" : "none" ;
});

logout.addEventListener(click_event,()=>{
  localStorage.removeItem("last_user");
});

var createroom=document.querySelector('#croom');
createroom.addEventListener(click_event,event);

function event()
{
      const request = new XMLHttpRequest();
      var channelName=prompt("Please enter a name for the channel")
      if(channelName===null)
      {
        return;
      }
      while(channelName==="")
      {
        alert("Enter a valid channelName")
        var channelName=prompt("Please enter a name for the channel")
      }
      request.open('POST','/ajax/room');
      const data=new FormData();
      data.append('name',channelName);
      request.send(data);
      request.onload=()=>{
        const response=request.responseText;
        if(response=='NOK')
        {
          alert("This channel name is aldready being used. Try a different name.")
          event();
        }
        else
        {
          alert("Channel created.")
          if(window.location.pathname=="/index")
          {
            location.reload();
          }
          else
          {
            window.location.pathname="/index";
          }
        }
    }
};


const template=Handlebars.compile(document.querySelector('#room').innerHTML)
document.addEventListener('DOMContentLoaded',myfunct);
function myfunct()
{
    const request=new XMLHttpRequest();
    request.open('GET','/ajax/room')
    request.onload=()=>{
        const response=JSON.parse(request.responseText);
        funct(response)
    }
    request.send();
};
