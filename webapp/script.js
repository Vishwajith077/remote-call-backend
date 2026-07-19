const API="https://remote-call-backend-1.onrender.com";

async function makeCall(){

    const numberInput=document.getElementById("number");
    const statusEl=document.getElementById("status");
    const number=numberInput.value.trim();

    if(!number){
        statusEl.innerText="Enter a phone number first";
        return;
    }

    statusEl.innerText="Sending...";

    try{
        const response=await fetch(API+"/call",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({
                number:number
            })

        });

        const result=await response.json();

        statusEl.innerText=result.message;

    }catch(err){
        // Network error, backend asleep/unreachable, CORS issue, etc.
        statusEl.innerText="Could not reach server: "+err.message;
    }

}