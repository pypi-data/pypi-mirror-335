import sys
import os
import shutil

try:
    import pylatex as pl
    from pylatex.utils import NoEscape
    import_error = False
except:
    import_error = True

# filepaths need to be identified with importlib_resources
# rather than __file__ as the latter does not work at runtime
# when the package is installed via pip install

if sys.version_info < (3, 9):
    # importlib.resources either doesn't exist or lacks the files()
    # function, so use the PyPI version:
    import importlib_resources
else:
    # importlib.resources has files(), so use that:
    import importlib.resources as importlib_resources

static = importlib_resources.files('miblab._static')
layout = importlib_resources.files('miblab.layout')
cover = str(static.joinpath('cover.jpg'))
epflreport = str(static.joinpath('epflreport.cls'))

#path = os.path.abspath("")

def force_move(src, dst):
    if os.path.exists(dst):
        os.remove(dst)
    os.rename(src, dst)

def force_copy(src, dst):
    if os.path.exists(dst):
        os.remove(dst)
    shutil.copy(src, dst)

def force_move_dir(src, dst):
    force_copy_dir(src, dst)
    shutil.rmtree(src)

def force_copy_dir(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def setup(
        reportpath,
        title='Title', 
        subtitle='Interim analysis', 
        subject='Subject',
        author='TRISTAN work package 2',
        affiliation='https://www.imi-tristan.eu/liver',  
        contact='Steven Sourbron',
        institute='University of Sheffield',
        department='Section of Medical Imaging and Technologies',
        email='s.sourbron@sheffield.ac.uk',      
    ):
    """Setup the report document.
    
    Parameters
    ----------
    reportpath : str
        Path to the folder where the report should be saved.
    title : str
        The title of the report.
    subtitle : str  
        The subtitle of the report.
    subject : str
        The subject of the report.
    author : str
        The author of the report.
    affiliation : str
        The affiliation of the author.
    contact : str
        The contact person for the report.
    institute : str
        The institute of the author.
    department : str
        The department of the author.
    email : str
        The email of the author.
        
    Returns
    -------             
    doc : pylatex.Document
        The report document.
    """
    if import_error:
        raise NotImplementedError(
            'Please install miblab as pip install miblab[report]'
            'to use this function.')
    dst = os.path.abspath("")
    outputpath = os.path.join(reportpath, 'report')
    force_copy(cover, os.path.join(dst, 'cover.jpg'))
    force_copy(epflreport, os.path.join(dst, 'epflreport.cls'))
    force_copy_dir(layout._paths[0], os.path.join(outputpath, 'layout'))
    doc = pl.Document()
    doc.documentclass = pl.Command('documentclass',"epflreport")
    makecover(doc, title, subtitle, subject, author, affiliation)
    titlepage(doc, reportpath, contact, institute, department, email)
    return doc


def makecover(
        doc: pl.Document, 
        title = 'Title', 
        subtitle = 'Interim analysis', 
        subject = 'Subject',
        author = 'TRISTAN work package 2',
        affiliation = 'https://www.imi-tristan.eu/liver',
    ):
    """Add a cover page to the report.
    
    Parameters
    ----------
    doc : pylatex.Document
        The report document.
    title : str
        The title of the report.
    subtitle : str  
        The subtitle of the report.
    subject : str
        The subject of the report.
    author : str
        The author of the report.
    affiliation : str
        The affiliation of the author.
    """
    if import_error:
        raise NotImplementedError(
            'Please install miblab as pip install miblab[report]'
            'to use this function.')
    # Cover page
    doc.append(NoEscape('\\frontmatter'))
    doc.append(pl.Command('title', title))
    doc.append(pl.Command('subtitle', subtitle))
    doc.append(pl.Command('author', author))
    doc.append(pl.Command('subject', subject))
    doc.append(pl.Command('affiliation', affiliation))
    doc.append(pl.Command('coverimage', 'cover.jpg')) 
    doc.append(pl.Command('definecolor', arguments = ['title','HTML','FF0000'])) # Color for cover title
    doc.append(NoEscape('\\makecover'))


def titlepage(
        doc:pl.Document, 
        reportpath,
        contact='Steven Sourbron',
        institute='University of Sheffield',
        department='Section of Medical Imaging and Technologies',
        email='s.sourbron@sheffield.ac.uk',
    ):
    """Add a title page to the report.

    Parameters
    ----------
    doc : pylatex.Document
        The report document.
    reportpath : str
        Path to the folder where the report should be saved.
    contact : str
        The contact person for the report.
    institute : str
        The institute of the author.
    department : str
        The department of the author.
    email : str
        The email of the author.

    Raises
    ------
    NotImplementedError
        If miblab is not installed.
    """

    if import_error:
        raise NotImplementedError(
            'Please install miblab as pip install miblab[report]'
            'to use this function.')
    # Title page
    doc.append(pl.Command('begin', 'titlepage'))
    doc.append(pl.Command('begin', 'center'))
    # Title
    doc.append(NoEscape('\\makeatletter'))
    doc.append(NoEscape('\\largetitlestyle\\fontsize{45}{45}\\selectfont\\@title'))
    doc.append(NoEscape('\\makeatother'))
    # Subtitle
    doc.append(NoEscape('\\linebreak'))
    doc.append(NoEscape('\\makeatletter'))
    doc.append(
        pl.Command(
            'ifdefvoid', 
            arguments=[
                NoEscape('\\@subtitle'),
                '',
                NoEscape('\\bigskip\\titlestyle\\fontsize{20}{20}\\selectfont\\@subtitle'),
            ]
        )
    )
    # Author
    doc.append(NoEscape('\\makeatother'))
    doc.append(NoEscape('\\linebreak'))
    doc.append(NoEscape('\\bigskip'))
    doc.append(NoEscape('\\bigskip'))
    doc.append('by')
    doc.append(NoEscape('\\linebreak'))
    doc.append(NoEscape('\\bigskip'))
    doc.append(NoEscape('\\bigskip'))
    doc.append(NoEscape('\\makeatletter'))
    doc.append(NoEscape('\\largetitlestyle\\fontsize{25}{25}\\selectfont\\@author'))
    doc.append(NoEscape('\\makeatother'))
    doc.append(NoEscape('\\vfill'))
    # Table with information
    doc.append(NoEscape('\\large'))
    with doc.create(pl.Tabular('ll')) as tab:
        tab.add_hline()
        tab.add_row(['Report compiled by: ', contact])
        tab.add_row(['Institute: ', institute])
        tab.add_row(['Department: ', department])
        tab.add_row(['Email: ', email])
        tab.add_row(['Date: ', NoEscape('\\today')])
        tab.add_hline()
    # TRISTAN logo
    with doc.create(pl.Figure(position='b!')) as pic:
        pic.append(pl.Command('centering'))
        im = os.path.join(reportpath, 'report', 'layout', 'tristan-logo.jpg')
        pic.add_image(im, width='2in')
    doc.append(pl.Command('end', 'center'))
    doc.append(pl.Command('end', 'titlepage'))


def build(
        doc: pl.Document, 
        filename, 
        reportpath,
    ):
    """Create the report.

    Parameters
    ----------
    doc : pylatex.Document
        The report document.
    filename : str
        The name of the report.
    reportpath : str
        Path to the folder where the report should be saved.

    Raises
    ------
    NotImplementedError
        If miblab is not installed.
    """
    if import_error:
        raise NotImplementedError(
            'Please install miblab as pip install miblab[report]'
            'to use this function.')
    path = os.path.abspath("")
    # Create report
    outputpath = os.path.join(reportpath, 'report')
    if not os.path.exists(outputpath):
        os.makedirs(outputpath)
    doc.generate_pdf(
        filename, 
        clean=False, 
        clean_tex=False, 
        compiler='pdfLaTeX', 
        compiler_args=['-output-directory', outputpath],
    )

    # Move all files to output folder and clean up
    force_move(os.path.join(path, 'cover.jpg'), os.path.join(outputpath, 'cover.jpg'))
    force_move(os.path.join(path, 'epflreport.cls'), os.path.join(outputpath, 'epflreport.cls'))
    force_move(os.path.join(path, filename+'.tex'), os.path.join(outputpath, filename+'.tex'))


