import cv2 as cv
from pyzbar.pyzbar import decode


def read_barcode(filepath: str) -> None:
    img = cv.imread(filepath)
    barcodes = decode(img)

    if not barcodes:
        raise ValueError("No barcodes detected.")

    for barcode in barcodes:
        (x, y, w, h) = barcode.rect
        cv.rectangle(img, (x - 10, y - 10), (x + w + 10, y + h + 10), (255, 0, 0), 2)

        print(f"{barcode.data = }")
        print(f"{barcode.type = }")

    cv.imshow("Image", img)
    cv.waitKey(0)
    cv.destroyAllWindows()


def main() -> None:
    filepath = "/home/blake/sift_keypoints.jpg"
    read_barcode(filepath)
    return


if __name__ == "__main__":
    main()
