<!DOCTYPE html>
<html>
<head>
  <title>Add Product</title>
  <script src="https://cdn.jsdelivr.net/jsbarcode/3.11.5/JsBarcode.all.min.js"></script>
  <style>
    .form-group {
      margin-bottom: 10px;
    }
    #barcodeImage {
      width: 300px;
      height: 80px;
      margin-top: 10px;
    }
  </style>
</head>
<body>
  <h2>Add Product</h2>

  <form method="POST">
    <div class="form-group">
      <label>Product Name:</label><br>
      <input type="text" name="name" required>
    </div>

    <div class="form-group">
      <label>Price:</label><br>
      <input type="number" step="0.01" name="price" required>
    </div>

    <div class="form-group">
      <label>Stock:</label><br>
      <input type="number" name="stock" required>
    </div>

    <div class="form-group">
      <label>Barcode (optional):</label><br>
      <input type="text" name="barcode" id="barcodeInput">
    </div>

    <div class="form-group">
      <button type="button" onclick="generateBarcode()">Generate Barcode</button>
    </div>

    <!-- Barcode number display -->
    <div id="barcodeNumberDisplay"></div>

    <!-- Where the barcode will show -->
    <svg id="barcodeImage"></svg>

    <div class="form-group">
      <button type="submit">Add Product</button>
    </div>
  </form>

  <p><a href="{{ url_for('dashboard') }}">Back to Dashboard</a></p>

  <script>
    function generateBarcode() {
      const barcodeInput = document.getElementById('barcodeInput');
      let barcodeValue = barcodeInput.value.trim();

      if (!barcodeValue) {
        // Generate random 12-digit barcode number
        barcodeValue = Math.floor(100000000000 + Math.random() * 900000000000).toString();
        barcodeInput.value = barcodeValue;
      }

      // Display the number
      document.getElementById("barcodeNumberDisplay").innerText = "Barcode: " + barcodeValue;

      // Generate the barcode
      JsBarcode("#barcodeImage", barcodeValue, {
        format: "CODE128",
        displayValue: false,
        width: 2,
        height: 60
      });
    }
  </script>
</body>
</html>
