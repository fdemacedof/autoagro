import cv2

# Carrega a imagem em escala de cinza ou colorida
img = cv2.imread('assets/pictures/kampu_1786998341.jpg')

# Converte para o espaço de cores LAB para alterar apenas a luminosidade
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
l, a, b = cv2.split(lab)

# Aplica o CLAHE no canal de luminosidade (L)
clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
cl = clahe.apply(l)

# Junta os canais de volta e converte para BGR
limg = cv2.merge((cl,a,b))
resultado = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

cv2.imwrite('resultado_clahe.jpg', resultado)