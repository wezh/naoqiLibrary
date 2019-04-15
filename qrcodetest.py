import qrcode

qr = qrcode.QRCode(version=1,
              error_correction=qrcode.ERROR_CORRECT_M,
              box_size=10,
              border=4,
              )
qr.add_data("Wenhao Zhu, e1600557, 3")
qr.make(fit=True)
img = qr.make_image()
img.save("./qrcodes/e1600557.png")

