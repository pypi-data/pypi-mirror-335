// Form handling
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contact-form');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(contactForm);
            const data = Object.fromEntries(formData);
            
            // Send data to backend
            fetch('/api/contact', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                // Show success message
                alert('Thank you for your message! I will get back to you soon.');
                
                // Reset form
                contactForm.reset();
            })
            .catch(error => {
                console.error('Error:', error);
                alert('There was an error sending your message. Please try again later.');
            });
        });
    }
    
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Load blog posts
    loadBlogPosts();
    
    // Load portfolio items
    loadPortfolioItems();
});

// Function to load blog posts
async function loadBlogPosts() {
    const blogGrid = document.getElementById('blog-posts');
    if (!blogGrid) return;

    try {
        // Fetch blog posts from the backend
        const response = await fetch('/api/blog-posts');
        const posts = await response.json();

        // Display blog posts
        posts.forEach(post => {
            const postElement = createBlogPostElement(post);
            blogGrid.appendChild(postElement);
        });
    } catch (error) {
        console.error('Error loading blog posts:', error);
    }
}

// Function to create blog post element
function createBlogPostElement(post) {
    const article = document.createElement('article');
    article.className = 'blog-post';
    
    article.innerHTML = `
        <div class="blog-post-content">
            <h3>${post.title}</h3>
            <p class="post-date">${new Date(post.date).toLocaleDateString()}</p>
            <p>${post.excerpt}</p>
            <div class="post-meta">
                <span class="source">${post.source}</span>
                <a href="${post.url}" target="_blank" rel="noopener noreferrer" class="read-more">Read More</a>
            </div>
        </div>
    `;
    
    return article;
}

// Function to load portfolio items
function loadPortfolioItems() {
    const portfolioGrid = document.querySelector('.portfolio-grid');
    if (!portfolioGrid) return;

    // Sample portfolio items
    const portfolioItems = [
        {
            title: 'E-commerce SEO Optimization',
            description: 'Improved search rankings and increased organic traffic by 200% for an e-commerce client.',
            image: 'portfolio-1.jpg',
            link: '#'
        },
        {
            title: 'Content Marketing Campaign',
            description: 'Developed and executed a content strategy that increased engagement by 150%.',
            image: 'portfolio-2.jpg',
            link: '#'
        },
        {
            title: 'Technical SEO Audit',
            description: 'Conducted comprehensive technical SEO audit and implemented improvements.',
            image: 'portfolio-3.jpg',
            link: '#'
        }
    ];

    // Display portfolio items
    portfolioItems.forEach(item => {
        const portfolioElement = createPortfolioElement(item);
        portfolioGrid.appendChild(portfolioElement);
    });
}

// Function to create portfolio element
function createPortfolioElement(item) {
    const article = document.createElement('article');
    article.className = 'portfolio-item';
    
    article.innerHTML = `
        <div class="portfolio-content">
            <img src="${item.image}" alt="${item.title}">
            <h3>${item.title}</h3>
            <p>${item.description}</p>
            <a href="${item.link}" class="btn primary">View Project</a>
        </div>
    `;
    
    return article;
}

// Intersection Observer for fade-in animations
const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in');
        }
    });
}, observerOptions);

// Observe all sections
document.querySelectorAll('section').forEach(section => {
    observer.observe(section);
}); 