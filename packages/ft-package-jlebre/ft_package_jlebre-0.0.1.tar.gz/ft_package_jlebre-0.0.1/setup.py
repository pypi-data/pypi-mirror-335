
import setuptools 
  
with open("README.md", "r") as fh: 
    description = fh.read() 
  
setuptools.setup( 
    name="ft_package_jlebre", 
    version="0.0.1", 
    author="jlebre", 
    author_email="jlebre@student.42lisboa.com", 
    packages=["ft_package"], 
    description="A sample test package", 
    long_description=open("README.md").read(), 
    long_description_content_type="text/markdown", 
    url="https://github.com/jlebre/42Python/P00/ex09/ft_package",
    license='MIT', 
    python_requires='>=3.6', 
    install_requires=[] 
) 
