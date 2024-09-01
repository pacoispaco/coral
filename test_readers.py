# This file contains Pytest-based unit tests for the SOF files module.

#import glob
import os
import pytest
import shlex
import shutil
import subprocess

# Constants
TOOLS_DIR = "./tools/"
SOF_READER = TOOLS_DIR + "sofreader.py"
IOC_READER = TOOLS_DIR + "iocreader.py"
SOURCE_DATA_DIR = "./data/"
JSON_DATA_DIR = "./testdata/"
SOF_DATA_DIR = SOURCE_DATA_DIR + "sof/"
SOF_JSON_DIR = JSON_DATA_DIR + "sof/"
IOC_DATA_DIR = SOURCE_DATA_DIR + "ioc/"
IOC_JSON_DIR = JSON_DATA_DIR + "ioc/"
SOF_DATA_FILE = SOF_DATA_DIR + "nl17-fixed.xlsx"
IOC_DATA_FILES = {"master_file": IOC_DATA_DIR + "master_ioc_list_v14.1.xlsx",
                  "multilingual_file": IOC_DATA_DIR + "Multiling\\ IOC\\ 14.1_b.xlsx",
                  "complementary_file": IOC_DATA_DIR + "IOC_Names_File_Plus-14.1.xlsx"}
READERS = [SOF_READER, IOC_READER]


@pytest.fixture
def set_up():
    print("\nFixture 'set_up'. Delete JSON data directories.")
    if os.path.exists(SOF_JSON_DIR):
        pass
        shutil.rmtree(SOF_JSON_DIR)
    if os.path.exists(IOC_JSON_DIR):
        pass
        shutil.rmtree(SOF_JSON_DIR)


@pytest.fixture
def clean_up():
    print("\nFixture 'clean_up'.")


def test_help(set_up, clean_up):
    """Test the help option of all readers."""
    for reader in READERS:
        command = f"./{reader} -h"
        completed_process1 = subprocess.run(shlex.split(command), capture_output=True, text=True)
        assert completed_process1.returncode == 0
        command = f"./{reader} --help"
        completed_process2 = subprocess.run(shlex.split(command), capture_output=True, text=True)
        assert completed_process2.returncode == 0
        assert completed_process1.stdout == completed_process2.stdout


def test_sof_ivd():
    """Test the information, verbose and dryrun options of the SOF reader."""
    command = f"./{SOF_READER} -ivd {SOF_DATA_FILE}"
    completed_process = subprocess.run(shlex.split(command), capture_output=True, text=True)
    assert completed_process.returncode == 0
    command = f"./{SOF_READER} -id {SOF_DATA_FILE}"
    completed_process = subprocess.run(shlex.split(command), capture_output=True, text=True)
    assert completed_process.returncode == 0
    output = """Dry-run: No taxonomy information will be written to files or to stdout
Taxonomy statistics:
  Taxonomy: SOF None
  Orders: 44
  Families: 253
  Species: 11196
  Total number of taxa: 11493\n"""
    assert completed_process.stdout == output


def test_sof_reader():
    """Test the SOF reader and its printing of the JSON taxonomy to stdout."""
    command = f"./{SOF_READER} {SOF_DATA_FILE}"
    completed_process = subprocess.run(shlex.split(command), capture_output=True, text=True)
    assert completed_process.returncode == 0


def test_sof_writer(set_up, clean_up):
    """Test the SOF reader and its writing of JSON files."""
    command = f"./{SOF_READER} -w -o {JSON_DATA_DIR} {SOF_DATA_FILE}"
    completed_process = subprocess.run(shlex.split(command), capture_output=True, text=True)
    assert completed_process.returncode == 0
    # Check that the output directory with JSON files was created
    assert os.path.exists(SOF_JSON_DIR)
    # Check that the number of JSON files is correct
#    print(glob.glob(JSON_DATA_DIR + "*json"))
#    assert len(glob.glob(JSON_DATA_DIR + "*json")) == 0 #11493
    # Check that it does not overwrite existing files and complains if they already exist
    command = f"./{SOF_READER} -w -o {JSON_DATA_DIR} {SOF_DATA_FILE}"
    completed_process = subprocess.run(shlex.split(command), capture_output=True, text=True)
    assert completed_process.returncode == 3
    # Clean up the JSON files.

def test_sof_loader():
    """Test the SOF reader and its loading of JSON files."""
    pass
    # First we need to read and write the JSON files.
#    command = f"./{SOF_READER} -li {SOF_DATA_FILE}"
#    completed_process = subprocess.run(shlex.split(command), capture_output=True, text=True)
#    assert completed_process.returncode == 0
    # Clean up the JSON files.


def test_ioc_ivd():
    """Test the information, verbose and dryrun options of the IOC reader."""
    command = (f"./{IOC_READER} -ivd -C{IOC_DATA_FILES['complementary_file']} "
               f"-M{IOC_DATA_FILES['multilingual_file']} {IOC_DATA_FILES['master_file']}")
    completed_process = subprocess.run(shlex.split(command),
                                       capture_output=True,
                                       text=True,
                                       shell=False)
    assert completed_process.returncode == 0
    command = (f"./{IOC_READER} -id -C{IOC_DATA_FILES['complementary_file']} "
               f"-M{IOC_DATA_FILES['multilingual_file']} {IOC_DATA_FILES['master_file']}")
    completed_process = subprocess.run(shlex.split(command),
                                       capture_output=True,
                                       text=True,
                                       shell=False)
    assert completed_process.returncode == 0
    print("==========")
    print(completed_process.stdout)
    print("==========")
    output = """Taxonomy statistics:
  Taxonomy: IOC None
  Infraclasses: 2
  Orders: 44
  Families: 253
  Genus: 2381
  Species: 11194
  Subspecies: 19802
  Total number of taxa: 33676\n"""
    assert completed_process.stdout == output


def test_ioc_reader():
    """Test the IOC reader and its printing of the JSON taxonomy to stdout."""
    command = (f"./{IOC_READER} -C{IOC_DATA_FILES['complementary_file']} "
               f"-M{IOC_DATA_FILES['multilingual_file']} {IOC_DATA_FILES['master_file']}")
    completed_process = subprocess.run(shlex.split(command),
                                       capture_output=True,
                                       text=True,
                                       shell=False)
    assert completed_process.returncode == 0
