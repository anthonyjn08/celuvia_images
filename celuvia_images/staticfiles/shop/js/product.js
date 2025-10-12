/*
Custom JavaScript for adding reviews on the  product detail page.

This will toggle the display of the review form when the user clicks
add review button.
*/

document.addEventListener("DOMContentLoaded", function () {
  const addReviewButton = document.getElementById("add-review");
  const reviewFormSection = document.getElementById("review-form");

  if (!addReviewButton || !reviewFormSection) return;

  // Hide form initially
  reviewFormSection.style.display = "none";

  addReviewButton.addEventListener("click", () => {
    reviewFormSection.style.display =
      reviewFormSection.style.display === "none" ? "block" : "none";
  });
});
