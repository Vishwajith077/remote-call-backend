const API="https://remote-call-backend-1.onrender.com";

async function makeCall(){

    const number=document.getElementById("number").value;

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

    document.getElementById("status").innerText=result.message;

}