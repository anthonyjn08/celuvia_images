/*
Custom JavaScript for editing or deleting reivews on theproduct detail page.

This allows users to update or delete their review within the product
detail page.
*/

document.addEventListener("DOMContentLoaded", function () {
  const reviews = document.querySelectorAll(".list-group-item[data-review-id]");

  reviews.forEach((review) => {
    const editBtn = review.querySelector(".edit-review");
    const editForm = review.querySelector(".edit-review-form");
    const cancelBtn = review.querySelector(".cancel-edit");
    const commentDisplay = review.querySelector(".review-comment");

    if (editBtn && editForm) {
      editBtn.addEventListener("click", () => {
        editForm.style.display = "block";
        commentDisplay.style.display = "none";
        editBtn.style.display = "none";
      });
    }

    if (cancelBtn) {
      cancelBtn.addEventListener("click", (e) => {
        e.preventDefault();
        editForm.style.display = "none";
        commentDisplay.style.display = "block";
        if (editBtn) editBtn.style.display = "inline-block";
      });
    }
  });
});
