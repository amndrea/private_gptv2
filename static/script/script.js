/**
 * Funzione che aggiunge dinamicamente i pulsanti alla pagina .
 * per decidere che tipo di domande visualizzare 
 * quando l'admin deve revisionarle
 */

function addPulsanti(){

    // Controllo se gli elementi sono gia presenti
    if (document.getElementById('customButtonsContainer')) {
        return;
    }

    const elementi = [
        {title: 'Domande non visualizzate', cosa: 'non_visualizzate'},
        {title: 'Vsualizzate da approvare', cosa: 'visualizzate_da_approvare'},
        {title: 'Gia approvate', cosa: 'approvate'},
        {title: 'Non apptovate', cosa: 'non approvate'}
    ];

    const container = document.createElement('div');
    container.style.textAlign = 'center'; 
    document.body.appendChild(container);
    container.appendChild(document.createElement('br'));


    for (const elemento of elementi){
        const heading = document.createElement('p');
        container.id = 'customButtonsContainer';
        heading.innerHTML = `${elemento.title}`;

        const link = document.createElement('a');
        link.href = `/ingestion/lista_risposte/${elemento.cosa}/`;
        link.style.backgroundColor = '#27408B';
        link.style.color = 'white';
        link.style.padding = '10px 20px';
        link.style.border = 'none';
        link.style.borderRadius = '5px';
        link.style.cursor = 'pointer';
        link.textContent = elemento.title;
        
        container.appendChild(heading);
        container.appendChild(link);
        container.appendChild(document.createElement('br'));
        container.appendChild(document.createElement('br'));
    }   
}