document.addEventListener('DOMContentLoaded', () => {
  const countryBoxes = document.querySelectorAll('.country-box');

  // Fade-in + scale animation using CSS class
  countryBoxes.forEach((box, index) => {
    setTimeout(() => {
      box.classList.add('visible');
    }, index * 120); // Staggered animation
  });

  countryBoxes.forEach(box => {
    const country = box.dataset.country;

    // Hover effect
    box.addEventListener('mouseenter', () => {
      box.classList.add('hovered');
      console.log(`You hovered on ${country}`);
    });

    box.addEventListener('mouseleave', () => {
      box.classList.remove('hovered');
    });

    // Click interaction
    box.addEventListener('click', () => {
      alert(`🌍 Welcome to the ${country} Live Pool!`);
    });
  });
});
