function funct(response)
{
    ch=Object.keys(response);
    contents={};
    ch.forEach(chn=>{
          if(response[chn].includes(user))
          {
                contents[chn]={'ch':chn,'admin':response[chn][0]};
          }
    });

    if(Object.keys(contents).length!==0)
    {
        document.querySelector('#head').innerHTML="Dashboard";
    }

    else
    {
        document.querySelector('#head').innerHTML="";
    }

    var chat=template({'contents':contents});
    document.querySelector('.list-group').innerHTML+=chat;
};

function myfn(channelName)
{
    window.location.pathname=`/roompage/${channelName}`
}

function redirectfn()
{
    window.location.pathname='/rooms'
}
