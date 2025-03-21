import tkinter as tk
from tkinter import messagebox

from calculator import wgs84_to_lest97, lest97_to_wgs84


try:
    # NB! Asenda see oma mooduli impordiga!
    from pyproj import Transformer
    
    def wgs84_to_lest97(latitude, longitude):
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:3301", always_xy=True)
        x, y = transformer.transform(longitude, latitude)
        return x, y
    
    def lest97_to_wgs84(x, y):
        transformer = Transformer.from_crs("EPSG:3301", "EPSG:4326", always_xy=True)
        longitude, latitude = transformer.transform(x, y)
        return latitude, longitude
        
except ImportError:
    messagebox.showerror("Viga", "Koordinaatide teisendamise moodulit ei leitud. Palun installige moodul.")

def main():
    root = tk.Tk()
    root.title("Koordinaatide teisendaja")
    

    direction_var = tk.IntVar(value=1)
    tk.Radiobutton(root, text="WGS84 → L-Est97", variable=direction_var, value=1).grid(row=0, column=0, sticky="w")
    tk.Radiobutton(root, text="L-Est97 → WGS84", variable=direction_var, value=2).grid(row=0, column=1, sticky="w")
    
    # Sisendväljad
    tk.Label(root, text="Sisendväärtus 1:").grid(row=1, column=0, sticky="w")
    input1 = tk.Entry(root)
    input1.grid(row=1, column=1)
    
    tk.Label(root, text="Sisendväärtus 2:").grid(row=2, column=0, sticky="w")
    input2 = tk.Entry(root)
    input2.grid(row=2, column=1)
    
    # Väljundväljad
    tk.Label(root, text="Väljundväärtus 1:").grid(row=3, column=0, sticky="w")
    output1 = tk.Entry(root)
    output1.grid(row=3, column=1)
    
    tk.Label(root, text="Väljundväärtus 2:").grid(row=4, column=0, sticky="w")
    output2 = tk.Entry(root)
    output2.grid(row=4, column=1)
    
  
    def convert():
        try:
            # võimaldab sisestada nii 59,123 kui 59.123)
            in1 = input1.get().replace(',', '.')
            in2 = input2.get().replace(',', '.')
            

            val1 = float(in1)
            val2 = float(in2)
            

            if direction_var.get() == 1:  # WGS84 → L-Est97
                x, y = wgs84_to_lest97(val1, val2)
                output1.delete(0, tk.END)
                output1.insert(0, f"{x:.2f}")
                output2.delete(0, tk.END)
                output2.insert(0, f"{y:.2f}")
            else:  # L-Est97 → WGS84
                lat, lon = lest97_to_wgs84(val1, val2)
                output1.delete(0, tk.END)
                output1.insert(0, f"{lat:.6f}")
                output2.delete(0, tk.END)
                output2.insert(0, f"{lon:.6f}")
                
        except ValueError:
            messagebox.showerror("Viga", "Vigane sisend. Palun sisestage arvud.")
        except Exception as e:
            messagebox.showerror("Viga", f"Teisendamine ebaõnnestus: {str(e)}")
    

    tk.Button(root, text="Teisenda", command=convert).grid(row=5, column=0, columnspan=2)
    
    # Sisendväljade siltide värskendamine vastavalt valitud suunale
    def update_labels():
        if direction_var.get() == 1:  # WGS84 → L-Est97
            root.grid_slaves(row=1, column=0)[0].config(text="Laiuskraad (N):")
            root.grid_slaves(row=2, column=0)[0].config(text="Pikkuskraad (E):")
            root.grid_slaves(row=3, column=0)[0].config(text="X koordinaat:")
            root.grid_slaves(row=4, column=0)[0].config(text="Y koordinaat:")
        else:  # L-Est97 → WGS84
            root.grid_slaves(row=1, column=0)[0].config(text="X koordinaat:")
            root.grid_slaves(row=2, column=0)[0].config(text="Y koordinaat:")
            root.grid_slaves(row=3, column=0)[0].config(text="Laiuskraad (N):")
            root.grid_slaves(row=4, column=0)[0].config(text="Pikkuskraad (E):")
    

    update_labels()

    direction_var.trace_add("write", lambda *args: update_labels())
    
    root.mainloop()


if __name__ == "__main__":
    main()
