// ensure script runs only after the entire HTML is ready.
document.addEventListener("DOMContentLoaded", function () {
  // Find all elements with the 'multi-searchable-select' class.
  const multiSelects = document.querySelectorAll(".multi-searchable-select");

  // Log to the console to confirm THIS NEW FILE is being executed.
  console.log("SUCCESS: custom.js version 1.1 is now running!");
  console.log(
    `Found ${multiSelects.length} elements to upgrade with Choices.js.`
  );

  multiSelects.forEach(function (element) {
    // Initialize Choices.js with the final, correct configuration.
    new Choices(element, {
      removeItemButton: true,
      searchPlaceholderValue: "Type to search...",
      placeholder: true,
      placeholderValue: `Select ${element.id.split("_")[0]}(s)...`,

      itemSelectText: "",
    });
  });
});
