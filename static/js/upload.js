


const sideMenu = document.querySelector('aside');
const menuBtn = document.querySelector('#menu_bar');
const closeBtn = document.querySelector('#close_btn');


const themeToggler = document.querySelector('.theme-toggler');



menuBtn.addEventListener('click',()=>{
       sideMenu.style.display = "block"
})
closeBtn.addEventListener('click',()=>{
    sideMenu.style.display = "none"
})

themeToggler.addEventListener('click',()=>{
     document.body.classList.toggle('dark-theme-variables')
     themeToggler.querySelector('span:nth-child(1').classList.toggle('active')
     themeToggler.querySelector('span:nth-child(2').classList.toggle('active')
})



const logoutButton = document.getElementById("logoutButton");
const dialogBox = document.getElementById("dialogBox");
const confirmLogout = document.getElementById("confirmLogout");
const cancelLogout = document.getElementById("cancelLogout");


logoutButton.addEventListener("click", () => {
    dialogBox.style.display = "flex";
});


confirmLogout.addEventListener("click", () => {
    alert("You have been logged out.");
    dialogBox.style.display = "none";
    
});


cancelLogout.addEventListener("click", () => {
    dialogBox.style.display = "none";
});






document.getElementById('uploadForm').onsubmit = async function (e) {
    e.preventDefault();
    
    let formData = new FormData();
    let fileInput = document.getElementById('upload');
    formData.append("file", fileInput.files[0]);

    const response = await fetch('/upload_file', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();
    const responseDiv = document.getElementById('response');
    //console.log(result);
    if (result.upload_status === 'success') {
        responseDiv.innerHTML = '<p>File uploaded successfully!</p>';
    } else if (result.upload_status === 'display_accounts') {
        responseDiv.innerHTML = '<p>Multiple accounts found. Please choose one:</p>';
        
        result.accounts.forEach(account => {
            const btn = document.createElement('button');
            btn.innerText = `Select Account: ${account.acc_no}`;
            btn.onclick = () => selectAccount(account.acc_no, result.file_document, result.document_type);
            responseDiv.appendChild(btn);
        });
    } else {
        responseDiv.innerHTML = `<p>Upload failed: ${result.upload_status}</p>`;
    }
};

async function selectAccount(account_no, file_document, document_type) {
    const response = await fetch('/confirm_account', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            account_no,
            file_document,
            document_type
        })
    });

    const result = await response.json();
    document.getElementById('response').innerHTML = `<p>${result.message}</p>`;
}