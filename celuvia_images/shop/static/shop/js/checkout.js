/*
Custom script for the checkout view.

If the user has a default address this is pre loaded in the shipping
address form. If the billing address is the same as the shipping address
then the shipping data is used for the billing address and the billing
address form is hidden
*/
document.addEventListener("DOMContentLoaded", function () {
  const sameBillingCheckbox = document.getElementById("same_billing");
  const billingSection = document.getElementById("billing-fields");
  if (!sameBillingCheckbox || !billingSection) return;

  const billingInputs = billingSection.querySelectorAll("input");
  const shippingInputs = document.querySelectorAll('[id^="id_shipping_"]');

  function toggleBilling() {
    if (sameBillingCheckbox.checked) {
      billingSection.style.display = "none";
      billingInputs.forEach((i) => (i.disabled = true));
      copyShippingToBilling();
    } else {
      billingSection.style.display = "block";
      billingInputs.forEach((i) => (i.disabled = false));
    }
  }

  function copyShippingToBilling() {
    billingInputs.forEach((b) => {
      const name = b.id.replace("id_billing_", "");
      const s = document.getElementById("id_shipping_" + name);
      if (s) b.value = s.value;
    });
  }

  sameBillingCheckbox.addEventListener("change", toggleBilling);
  shippingInputs.forEach((i) =>
    i.addEventListener("input", copyShippingToBilling)
  );

  toggleBilling();
});
