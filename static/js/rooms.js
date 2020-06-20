
function funct(response)
{
    ch=Object.keys(response);
    var contents={}
    ch.forEach(chn=>{
      if(!response[chn].includes(user))
      {
            contents[chn]={'ch':chn,'admin':response[chn][0]};
      }
    });
    var chat=template({'contents':contents});
    document.querySelector('.list-group').innerHTML=chat;
};

function fn(channelName)
{
    const request=new XMLHttpRequest();
    request.open('POST','/ajax/participants')

    const data=new FormData();
    data.append('name',channelName);
    request.send(data);

    request.onload=()=>{
        const response=request.responseText;
        if(response=='OK')
        {
          alert('You are added to this channel')
          window.location.pathname='/index';
        }
    }
}
