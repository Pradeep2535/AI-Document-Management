const  sideMenu = document.querySelector('aside');
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



const result = [
    {
        account_number: "123456789",
        name: "John Doe",
        uploaded_date: "2025-01-05",
        uploaded_time: "10:30 AM",
        uploaded_documents: "Document1.pdf",
    },
    {
        account_number: "987654321",
        name: "Jane Smith",
        uploaded_date: "2025-01-06",
        uploaded_time: "2:45 PM",
        uploaded_documents: "Document2.jpg",
    }
];


function populateTransactionTable(data) {
    const tableBody = document.querySelector('.transaction-table tbody');
    tableBody.innerHTML = ""; 

    data.forEach((transaction) => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${transaction.account_number}</td>
            <td>${transaction.uploaded_date}</td>
            <td>${transaction.name}</td>
            <td>${transaction.uploaded_time}</td>
            <td>${transaction.uploaded_documents}</td>
        `;
        
        tableBody.appendChild(row);
    });
}


populateTransactionTable(result);
