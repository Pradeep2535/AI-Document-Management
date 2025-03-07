




















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