// ensure script runs only after the entire HTML is ready.
document.addEventListener("DOMContentLoaded", function () {
  // --- Store all Choices instances in an array ---
  const choicesInstances = [];

  // Find all elements with the 'multi-searchable-select' class.
  const multiSelects = document.querySelectorAll(".multi-searchable-select");

  // Log to the console to confirm THIS NEW FILE is being executed.
  console.log("SUCCESS: custom.js version 1.1 is now running!");
  console.log(
    `Found ${multiSelects.length} elements to upgrade with Choices.js.`
  );

  multiSelects.forEach(function (element) {
    // Initialize Choices.js with the final, correct configuration.
    const choices = new Choices(element, {
      removeItemButton: true,
      searchPlaceholderValue: "Type to search...",
      placeholder: true,
      placeholderValue: `Select ${element.id.split("_")[0]}(s)...`,

      itemSelectText: "",
    });
    // Push the created instance into our array for later use
    choicesInstances.push(choices);
  });

  // Get the reset button by its ID
  const resetButton = document.getElementById("reset-filters-btn");

  if (resetButton) {
    // Add a click event listener
    resetButton.addEventListener("click", function () {
      console.log("Reset button clicked. Clearing all selections.");

      // Loop through all our stored Choices instances
      choicesInstances.forEach(function (instance) {
        // Use the official API method to remove all selected items
        instance.removeActiveItems();
      });
    });
  }
});
