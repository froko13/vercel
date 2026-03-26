class Carousel {
    constructor() {
        this.carousel = document.getElementById('carousel');
        this.container = document.getElementById('carouselContainer');
        this.slides = Array.from(this.carousel.children);
        this.currentIndex = 0;
        this.cardSize = 270; // Ширина одной карточки для скролла
        this.init();
    }
    
    init() {
        this.positionSlides();
        this.bindEvents();
    }
    
    positionSlides() {
        this.slides.forEach((slide, index) => {
            slide.style.transform = `translateX(${this.cardSize * index}px)`;
        });
    }
    
    handleWheel(e) {
        e.preventDefault();
        if (e.deltaY > 0) {
            this.next();
        } else {
            this.prev();
        }
    }
    
    goToSlide(index) {
        this.currentIndex = index;
        const targetPosition = this.cardSize * index;
        this.carousel.style.transform = `translateX(-${targetPosition}px)`;
    }
    
    next() {
        if (this.currentIndex < this.slides.length - 1) {
            this.goToSlide(this.currentIndex + 1);
        }
    }   
    
    prev() {
        if (this.currentIndex > 0) {
            this.goToSlide(this.currentIndex - 1);
        }
    }
    
    bindEvents() {
        this.container.addEventListener('wheel', (e) => this.handleWheel(e), { passive: false });
        }
}
    
document.addEventListener('DOMContentLoaded', () => {
    new Carousel();
});