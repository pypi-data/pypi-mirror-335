import numpy as np 
import pyperclip 
import matplotlib.pyplot as plt 
import numpy as np 
import mplcursors 
from itertools import cycle 
import os 
import numpy as np 
import pandas 
import webbrowser 

snp_names = ["snp","rsid","rsids","snps"] 

class snp(): 
    def __init__(self,rsid): 
        self.rsid = rsid 
    
    def websearch(self): 
        

        # URL to open
        url = f"{self.rsid}" 

        # Open URL in default browser
        webbrowser.open(url)

        # To specify a browser, you might need to configure a path or use a browser alias:
        # webbrowser.get('chrome').open(url)

    
    def __repr__(self) -> str: 
        name = "" 
        for attr in list(self.__dict__.keys()): 
            name += f"{attr}: {getattr(self,attr)}\n" 
        return name 
        pass

class file(): 
    def __init__(self,group,path,sheet=""): 

        if "csv" in path: 
            self.file =pandas.read_csv(path) 
        elif "tsv" in path: 
            self.file = pandas.read_csv(path,sep="\t") 
        elif "xlsx" in path: 
            self.file  = pandas.read_excel(path,sheet_name = sheet) 
        else:
            print("Error: Only CSV, TSV, or Excel accepted. ") 
        
        self.columnnames = self.file.columns.to_list() 
        self.atts = [] 
        self.group = group 
        group_atts = self.group.atts 
        # print(self.columnnames) 
        

        for i in self.columnnames:
            setattr(self,i,self.file[i]) if i.lower() not in snp_names else setattr(self,"rsids",self.file[i]) 
            self.atts.append(i) if i.lower() not in snp_names else self.atts.append("rsids") 
            group_atts.append(i) if i not in group_atts else None 

        if hasattr(self,"rsids"): 
            pass 
        else: 
            print("Error: no rsid column found. ") 
            

    def build_snps(self):
        group_snps = self.group.snps 
        self.snps = [] 
        for i in range(0,len(self.rsids)): 
            variant = getsnpbyrsid(self.rsids[i],group_snps) 
            if variant == None: 
                variant = snp(self.rsids[i]) 
                group_snps.append(variant) 
            for s in self.atts: 
                value = getattr(self,s).tolist() [i] 
                # print(value)
                setattr(variant,s,value) if s not in snp_names else None 
            self.snps.append(variant) 

class filegroup(): 
    def __init__(self,paths=dict): 
        self.files = [] 
        self.snps = [] 
        self.atts = [] 
        for i in paths: 
            s = file(self,i,paths[i]) 
            self.files.append(s) 
        for file_instance in self.files: 
            file_instance.build_snps() 
    
        
    def save(self,filename,atts): 
        output = open(filename,"w")
        a = "" 
        for s in atts: 
            # output.write(str(i)) 
            a += f"{s}\t" 
        output.write(a+"\n") 
        for i in self.snps: 
            a = "" 
            for s in atts: 
                try:
                    a += str(getattr(i,s) ) + "\t" 
                    # output.write(f"{i.rsid}\t{a}\n") 
                except: 
                    pass 
            output.write(a + "\n") if a != "" else None 
        output.close() 

            

    def plot(self,xattr,yattr,xlabel,ylabel,logarithmic=bool,title=str,show=bool,save=""): # save=".format" 
        snps = self.snps 
        if xattr.lower() in snp_names: 
            xattr = "rsid" 
            xlabel = "rsid" 
        if yattr.lower() in snp_names: 
            yattr = "rsid" 
            ylabel = "rsid" 

        snpstoplot = [] 

        for i in snps:
            if hasattr(i,xattr) and hasattr(i,yattr): 
                snpstoplot.append(i) 
        
        create_scatter_plot([snpstoplot],title,xattr,yattr,xlabel,ylabel,show,save,logarithmic) 

        # if type == "Beta": 
        #     create_scatter_plot_Betas(snpstoplot,title,xattr,yattr,show,save,type) 
        # # elif type == "pValue": 
        # #     create_scatter_plot_pValues(snpstoplot,title,xattr,yattr,show,save,type) 
        # else:
        #     print("Error Type ") 
    
def getsnpbyrsid(rsid,group): 
    for i in group:
        if i.rsid == rsid: 
            return i 
        else: 
            pass 

# Function to input values and create scatter plot
def create_scatter_plot(snps_list,title,xattr,yattr,xlabel,ylabel,show,save,logarithmic): 
    colors = [
        ("Green", (0, 255, 0)),
        ("Cyan", (0, 255, 255)),
        ("Red", (255, 0, 0)),
        ("Blue", (0, 0, 255)),
        ("Yellow", (255, 255, 0)),
        ("Magenta", (255, 0, 255)),
        ("White", (255, 255, 255)),
        ("Black", (0, 0, 0)),
        ("Gray", (128, 128, 128)),
        ("Light Gray", (211, 211, 211)),
        ("Dark Gray", (169, 169, 169)),
        ("Orange", (255, 165, 0)),
        ("Purple", (128, 0, 128)),
        ("Brown", (165, 42, 42)),
        ("Pink", (255, 192, 203)),
        ("Lime", (50, 205, 50)),
        ("Teal", (0, 128, 128)),
        ("Navy", (0, 0, 128)),
        ("Olive", (128, 128, 0)),
        ("Maroon", (128, 0, 0))
    ] 
    # colors = cycle(colors) 
    colors = cycle([f'#{r:02x}{g:02x}{b:02x}' for _, (r, g, b) in colors])

    scatterdict = {}
    print("Warning: multiple plots detected! Selection may not work as intended!") if len(snps_list) != 1 else None
    for snps in snps_list:
        x = [] 
        y = [] 

        if logarithmic:  # Assuming 'logarithmic' is a boolean flag
            for variant in snps: 
                x.append(-1 * np.log10(getattr(variant, xattr)) ) 
                y.append(-1 * np.log10(getattr(variant, yattr)) )
        else: 
            for variant in snps: 
                x.append(getattr(variant, xattr) ) 
                y.append(getattr(variant, yattr) ) 

        scatter = plt.scatter(x, y, color=next(colors))
        cursor1 = mplcursors.cursor(scatter, hover=True)
        cursor2 = mplcursors.cursor(scatter, hover=False)

        scatterdict[(cursor1,cursor2)] = snps


    for cursortuple, snps in scatterdict.items():
        cursortuple[0].connect(
            "add", 
            lambda sel, snps=snps: sel.annotation.set_text(
                f'RSID: {process(snps[sel.index], xattr, yattr, xlabel, ylabel, logarithmic, False)}'
            )
        ) 
        cursortuple[1].connect(
            "add", 
            lambda sel, snps=snps: sel.annotation.set_text(
                f'RSID: {process(snps[sel.index], xattr, yattr, xlabel, ylabel, logarithmic, True)}'
            )
        ) 

        
    # Create scatter plot
    # scatter_plots.append(plt.scatter(x, y, color=next(colors)) ) 
    
    # for scatter in scatter_plots: 
    # Add interactive annotations
    xlabel = xlabel 
    ylabel = ylabel 
    if logarithmic: 
        xlabel = f'-1 * log10({xlabel})' 
        ylabel = f'-1 * log10({ylabel})' 

    # Add labels and title
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    # Show the plot
    plt.show() if show else None 
    plt.savefig(os.getcwd() + '/' + title+save) if save else None 

def process(snp,xattr,yattr,xlabel,ylabel,logarithmic,websearch): 
    pyperclip.copy(snp.rsid) 
    if not(websearch): 
        a = "rsid" 
        if logarithmic: 
            return f"{getattr(snp,a)}\n {xlabel}: {-1*np.log10(float(getattr(snp,xattr)))}\n {ylabel}: {-1*np.log10(float(getattr(snp,yattr)))}" 
        else: 
            return f"{getattr(snp,a)}\n {xlabel}: {((getattr(snp,xattr)))}\n {ylabel}: {((getattr(snp,yattr)))}" 
        # print(snps.index(getsnpbyrsid("rs540836853",snps)))  \n {sel.index} 
        # 
    else: 
        snp.websearch() 
        a = "rsid" 
        if logarithmic: 
            return f"{getattr(snp,a)}\n {xlabel}: {-1*np.log10(float(getattr(snp,xattr)))}\n {ylabel}: {-1*np.log10(float(getattr(snp,yattr)))}" 
        else: 
            return f"{getattr(snp,a)}\n {xlabel}: {((getattr(snp,xattr)))}\n {ylabel}: {((getattr(snp,yattr)))}" 
        # print(snps.index(getsnpbyrsid("rs540836853",snps)))  \n {sel.index} 
        # 

def getcommonsnps(data): 
    commonsnps= [] 
    for variant in data.snps: 
        common = True 
        for file_object in data.files:
            if not(variant in file_object.snps): 
                common = False 
        if common: 
            commonsnps.append(variant) 
    return commonsnps 

def parsepaths(file_paths): 
    filedict = {} 
    for file in file_paths:
        filedict[file] = "" 
    return filedict 
    data = filegroup(paths=filedict) 
    return data 

def generatefilename(paths): 
    filename= "" 
    for path in paths:
        pathparts = path.split('/') 
        filename += pathparts[-1+len(pathparts)].split('.')[0] 
    return filename 


