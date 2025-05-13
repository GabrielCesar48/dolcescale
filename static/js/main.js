/* static/js/main.js */

document.addEventListener('DOMContentLoaded', function() {
    // ===== Variáveis globais =====
    const navbar = document.querySelector('.navbar');
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    // ===== Loading Spinner =====
    function showLoader() {
        // Criar o elemento de spinner se não existir
        if (!document.querySelector('.spinner-wrapper')) {
            const spinnerWrapper = document.createElement('div');
            spinnerWrapper.className = 'spinner-wrapper';
            
            const spinner = document.createElement('div');
            spinner.className = 'spinner-coffee';
            
            spinnerWrapper.appendChild(spinner);
            document.body.appendChild(spinnerWrapper);
        } else {
            document.querySelector('.spinner-wrapper').style.display = 'flex';
        }
    }
    
    function hideLoader() {
        const spinner = document.querySelector('.spinner-wrapper');
        if (spinner) {
            spinner.style.opacity = '0';
            spinner.style.visibility = 'hidden';
            
            // Remover após a transição
            setTimeout(() => {
                spinner.style.display = 'none';
            }, 500);
        }
    }
    
    // Mostrar loader quando a página carrega
    showLoader();
    
    // Esconder loader quando a página estiver carregada
    window.addEventListener('load', () => {
        setTimeout(() => {
            hideLoader();
        }, 500); // Pequeno atraso para suavizar a experiência
    });
    
    // ===== Navbar Scroll Effect =====
    function handleNavbarScroll() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    }
    
    window.addEventListener('scroll', handleNavbarScroll);
    
    // Inicializa o estado da navbar
    handleNavbarScroll();
    
    // ===== Fecha o menu ao clicar em um link (em mobile) =====
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth < 992 && navbarCollapse.classList.contains('show')) {
                navbarToggler.click();
            }
        });
    });
    
    // ===== Smooth Scroll para âncoras =====
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80, // Ajuste para a altura da navbar
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // ===== Botão de voltar ao topo =====
    const createScrollTopButton = () => {
        const scrollTopButton = document.createElement('div');
        scrollTopButton.className = 'scroll-to-top';
        scrollTopButton.innerHTML = '<i class="bi bi-arrow-up"></i>';
        document.body.appendChild(scrollTopButton);
        
        scrollTopButton.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
        
        // Mostrar/esconder botão baseado no scroll
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                scrollTopButton.classList.add('show');
            } else {
                scrollTopButton.classList.remove('show');
            }
        });
    };
    
    createScrollTopButton();
    
    // ===== Animações ao Scroll =====
    function animateOnScroll() {
        const elements = document.querySelectorAll('.card, .stats-number, h2, .divider');
        
        elements.forEach(element => {
            // Adiciona classe para preparar a animação se ainda não tiver
            if (!element.classList.contains('fade-in-up') && !element.classList.contains('has-animation')) {
                element.classList.add('has-animation');
                element.style.opacity = '0';
                element.style.transform = 'translateY(20px)';
                element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            }
            
            // Verifica se o elemento está visível na viewport
            const rect = element.getBoundingClientRect();
            const windowHeight = window.innerHeight || document.documentElement.clientHeight;
            
            if (rect.top <= windowHeight * 0.85 && rect.bottom >= 0) {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        });
    }
    
    // Executa a animação ao carregar a página e durante o scroll
    window.addEventListener('load', animateOnScroll);
    window.addEventListener('scroll', animateOnScroll);
    
    // ===== Animar tabela do cronograma =====
    function animateTable() {
        const tableRows = document.querySelectorAll('.table tbody tr');
        
        tableRows.forEach((row, index) => {
            row.style.opacity = '0';
            row.style.transform = 'translateY(10px)';
            row.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            
            // Atraso escalonado para cada linha
            setTimeout(() => {
                row.style.opacity = '1';
                row.style.transform = 'translateY(0)';
            }, 100 + (index * 50));
        });
    }
    
    // Animar tabela quando estiver visível
    const observeTable = () => {
        const table = document.querySelector('.table');
        if (table) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        animateTable();
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.2 });
            
            observer.observe(table);
        }
    };
    
    window.addEventListener('load', observeTable);
    
    // ===== Efeito de pulsação nos botões de marcar concluído =====
    const pulsateCompletedButtons = () => {
        const buttons = document.querySelectorAll('.btn-outline-success');
        
        buttons.forEach(button => {
            button.classList.add('animated-bg');
            
            // Adicionar efeito de pulsação suave
            setInterval(() => {
                button.classList.add('pulse');
                setTimeout(() => {
                    button.classList.remove('pulse');
                }, 1000);
            }, 5000);
        });
    };
    
    window.addEventListener('load', pulsateCompletedButtons);
    
    // ===== Notificações Toast =====
    const createToast = (message, type = 'info') => {
        // Verifique se o container de toasts já existe
        let toastContainer = document.querySelector('.toast-container');
        
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        // Criar o toast
        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header bg-${type} text-white">
                    <i class="bi bi-info-circle me-2"></i>
                    <strong class="me-auto">DolceScale</strong>
                    <small>Agora</small>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        // Inicializar e mostrar o toast
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            delay: 5000
        });
        
        toast.show();
        
        // Remover depois que for escondido
        toastElement.addEventListener('hidden.bs.toast', function () {
            toastElement.remove();
        });
    };
    
    // Exemplo de uso do toast para alertas do sistema
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        alerts.forEach(alert => {
            const message = alert.textContent.trim();
            const type = alert.classList.contains('alert-success') ? 'success' : 
                        alert.classList.contains('alert-danger') ? 'danger' : 
                        alert.classList.contains('alert-warning') ? 'warning' : 'info';
            
            setTimeout(() => {
                createToast(message, type);
            }, 1000);
            
            // Opcional: ocultar o alerta original
            setTimeout(() => {
                alert.style.display = 'none';
            }, 500);
        });
    }
    
    // ===== Contador animado para números estatísticos =====
    const animateCounters = () => {
        const counters = document.querySelectorAll('.stats-number');
        
        counters.forEach(counter => {
            const target = parseInt(counter.textContent, 10);
            counter.textContent = '0';
            
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        let count = 0;
                        const updateCount = () => {
                            const increment = Math.ceil(target / 50);
                            
                            if (count < target) {
                                count = Math.min(count + increment, target);
                                counter.textContent = count;
                                requestAnimationFrame(updateCount);
                            }
                        };
                        
                        requestAnimationFrame(updateCount);
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.5 });
            
            observer.observe(counter);
        });
    };
    
    window.addEventListener('load', () => {
        setTimeout(animateCounters, 1000);
    });
});