
function switchPanel(activePanelId) {
    const panels = ['stocksCompany', 'GlassPanel'];
    const buttons = {
        'stocksCompany': document.querySelector('.PanelText'),
        'GlassPanel': document.querySelector('.PanelGlassTwo')
    };

    panels.forEach(panelId => {
        const panel = document.getElementById(panelId);
        if (panel) {            
            panel.classList.remove('active-panel');
            panel.classList.add('hidden');
        }
    });


    const activePanel = document.getElementById(activePanelId);
    if (activePanel) {  
        activePanel.classList.remove('hidden');
        activePanel.classList.add('active-panel');
    }

    Object.keys(buttons).forEach(key => {
        if (buttons[key]) {
            if (key === activePanelId) {
                buttons[key].classList.add('active');
            } else {
                buttons[key].classList.remove('active');
            }
        }
    });


    const glass = document.querySelector('.Glass');
    const stripeAsideTwo = document.querySelector('.StripeAsideTwo');
    
    if (activePanelId === 'GlassPanel') {
        glass?.classList.add('active');
        stripeAsideTwo?.classList.add('active');
    } else {
        glass?.classList.remove('active');
        stripeAsideTwo?.classList.remove('active');
    }
}


document.addEventListener('DOMContentLoaded', function() {
    switchPanel('stocksCompany');
    
    const dropdownTrigger = document.querySelector('.dropdownTrigger');
    const dropdownMenu = document.querySelector('.DropdownMenu');
    const stocksCompany = document.querySelector('.stocksCompany');

    dropdownTrigger?.addEventListener('click', function(e) {
        e.stopPropagation(); 
        dropdownMenu.classList.toggle('active');
    });

    document.addEventListener('click', function(e) {
        if (!stocksCompany.contains(e.target)) {
            dropdownMenu.classList.remove('active');
        }
    });

    document.querySelectorAll('.DropdownMenu li')?.forEach(li => {
        li.addEventListener('click', function(e) {
            e.stopPropagation();
            document.querySelector('.dropdownTrigger span').textContent = this.textContent;
            dropdownMenu.classList.remove('active');
        });
    });
})