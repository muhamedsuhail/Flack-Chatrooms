var user=document.querySelector("#us").innerHTML
var channelName=document.querySelector('#chname').innerHTML;
var backicon=document.querySelector('.icon');
var textarea=document.querySelector('textarea');
var messages=document.querySelector('.messages');
var html=document.querySelector('html');
var body=document.querySelector('body');
var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
var click_event=(/iPhone|iPad|iPod|Android/i.test(navigator.userAgent))? 'touchstart':'click';

//Stores the last visited channelName to localStorage for retrieval of previous session.

localStorage.setItem("last_room",channelName);

backicon.addEventListener(click_event,
function event()
{
      localStorage.removeItem("last_room");
      window.location.pathname='/index';
});


textarea.addEventListener('keydown', event=>{

  if(event.keyCode==13){

    //Send the message when user presses ENTER key.

    document.querySelector('#submit').click();
  }

  setTimeout(function() {

    //Grow textarea when typing to an extent and then make the textarea scrollable.

    textarea.style.cssText = 'height:auto';
    var height = Math.min(20 * 5, textarea.scrollHeight+2);

    if(height>48)
    {
      textarea.style.cssText = 'height:' + height + 'px';
    }

  },0);

});

document.addEventListener('DOMContentLoaded',()=>{

    //Ajax request to fetch all the previously stored messages of the channel.

    const request=new XMLHttpRequest();
    const template=Handlebars.compile(document.querySelector('#temp').innerHTML)
    request.open('GET',`/messages/${channelName}`)
    request.onload=()=>{

      if(request.responseText!='0')
      {
        //Display all the messages to the roompage.

        const response=JSON.parse(request.responseText);
        console.log(response)
        for(let i of response)
        {
            i["flag"]=user==i.user ?  true:false;
            const message=template({'contents':i})
            messages.innerHTML+=message;
        }
        addClickHandler();
        html.scrollTop=messages.scrollHeight;
        body.scrollTop=messages.scrollHeight;

      }
    }
    request.send();

    //reset textarea
    textarea.value="";

    //Broadcast new message to socket.

    socket.on('connect', ()=>{
        var text=document.querySelector('form');
        text.addEventListener('submit',e=>{

            //Prevent default form submit action.
            e.preventDefault();
            const message=document.querySelector('#text-area').value.trim();
            if(message.length!=0)
            {
                const datenow=new Date();
                date=datenow.getDate()+' '+datenow.toLocaleString('defult', { month: 'short' })+' '+datenow.getFullYear();
                time=datenow.toLocaleString('default',{hour:'numeric',minute:'numeric',hour12:true})
                socket.emit('new message',{'channelName':channelName,'user':user,'message':message,'date':date,'time':time});
                text.reset();
            }
        });


    });
    var flag=false;

    //Update broadcasted messages to DOM.

    socket.on('message received',data=>{

      //flag monitors the scroll position. Window scrolls automatically on new messages.

      flag=(window.pageYOffset+html.clientHeight)>=html.scrollHeight-(html.clientHeight) ? true:false ;
      if(data.channelName==channelName)
      {
          data["flag"]=user==data.user ?  true:false;
          const message=template({'contents':data})
          messages.innerHTML+=message;
          addClickHandler();
          if(flag)
          {
            html.scrollTop=messages.scrollHeight;
            body.scrollTop=messages.scrollHeight;
            flag=false;
          }
      }
    });
    socket.on('msg_deleted',function(data){

        //Delete messages by msg_id (PRIMARY_KEY).

        var cont=messages.querySelectorAll('.cont');
        cont.forEach(function(chat_bubble)
        {
            var id=+(chat_bubble.id);
            if(data['msg_id']==id)
            {
                chat_bubble.remove();
            }
        });
    });

});

//Thrash can click event handler.

function addClickHandler()
{
    if(!!messages.querySelectorAll('.container2'))
    {
      var cont=messages.querySelectorAll('.container2');
      cont.forEach(function(chat_bubble)
      {
          var delete_icon=chat_bubble.querySelector('#delete')
          var id=+(chat_bubble.id);
          delete_icon.addEventListener(click_event,function(event)
          {
              event.stopPropagation();event.preventDefault();
              delete_icon.click();
              var txt=confirm("Are you sure you want to delete this message?")
              if(txt==true)
              {
                  socket.emit('delete_msg',{'channelName':channelName,'msg_id':id})
              }
          });

      });
    }
}
