import shutil
import logging
import filecmp
import pydicom
from uuid import uuid4
from pathlib import Path
from zoneinfo import ZoneInfo
from datetime import datetime

logger = logging.getLogger(__name__)

class Sorter:
    def __init__(self, dcmfile: Path, archive: Path):
        self._dcmfile = dcmfile
        self._archive = archive
        self._mode = 0o0750
        self._group = 'mrimgmt'
        self._timezone = 'America/New_York'

    def sort(self):
        try:
            self._sort()
        except Exception as e:
            logger.exception(e)

    def _sort(self):
        ds = pydicom.dcmread(self._dcmfile)
        stem = self._get_stem(ds)
        project = self._get_project(ds)
        session = self._get_session(ds)
        projectdir = self._archive / project
        sessiondir = projectdir / session
        destfile = sessiondir / f'{stem}.dcm'
        logger.info(f'generated archive file name {destfile}')
        self._mkdir(projectdir)
        self._mkdir(sessiondir)
        try:
            logger.debug(f'comparing {self._dcmfile} to {destfile}')
            self._compare(self._dcmfile, destfile)
        except FileConflictError as e:
            logger.error(e)
            raise e
        except FileNotFoundError:
            pass
        logger.info(f'renaming {self._dcmfile} to {destfile}')
        self._dcmfile.rename(destfile)

    def _compare(self, a, b):
        if not filecmp.cmp(a, b):
            raise FileConflictError(f'{a} not identical to {b}')

    def _mkdir(self, d):
        d.mkdir(parents=True, exist_ok=True)
        if self._mode:
            logger.debug(f'setting mode on {d} to {self._mode}')
            d.chmod(self._mode)
        if self._group:
            logger.debug(f'setting group ownership on {d} to {self._group}')
            shutil.chown(d, group=self._group)

    def _get_stem(self, ds):
        parts = list()
        patient = ds.get('PatientID', 'UNKNOWN').strip()
        modality = ds.get('Modality', '').strip()
        series = str(ds.get('SeriesNumber', '')).strip()
        instance = str(ds.get('InstanceNumber', '')).strip()
        uid = self._get_unique_id(ds)
        if patient:
            parts.append(patient)
        if modality:
            parts.append(modality)
        if series:
            parts.append(series)
        if instance:
            parts.append(instance)
        parts.append(uid)
        return '.'.join(parts)

    def _get_datetime(self, ds):
        tzinfo = ZoneInfo(self._timezone)
        date = datetime.now(tz=tzinfo).strftime('%Y%m%d')
        time = datetime.now(tz=tzinfo).strftime('%H%M%S')
        date = ds.get('StudyDate', today).strip()
        time = ds.get('StudyTime') 
        
    def _get_unique_id(self, ds):
        result = ds.get('SOPInstanceUID', '').strip()
        if not result:
            logger.warning('could not find SOPInstanceUID, using uuid4')
            result = str(uuid4())
        return result

    def _get_project(self, ds):
        project = ds.get('StudyDescription', 'UNKNOWN').strip()
        return project.upper()

    def _get_session(self, ds):
        session = ds.get('PatientID', '').strip()
        if not session:
            logger.info(f'could not find PatientID, trying StudyInstanceUID')
            session = ds.get('StudyInstanceUID', '').strip()
        if not session:
            logger.info('could not find StudyInstanceUID, using timestamp')
            now = datetime.now()
            session = now.isoformat()
        return session

class FileConflictError(Exception):
    pass

