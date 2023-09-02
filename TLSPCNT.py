import os
from ctypes import cdll, c_long, c_uint32, c_uint16,byref,create_string_buffer, \
                    c_bool, c_char_p,c_int,c_int16, c_int32,c_double, \
                    sizeof,c_voidp

class TLSPCNT:
    def __init__(self,dll_path=r'C:\Program Files\IVI Foundation\VISA\Win64\Bin'):
        self.dll = cdll.LoadLibrary(os.path.join(dll_path,'TLSPCNT_64.dll'))

        self.devSession = c_long()
        self.devSession.value = 0

    def __testForError(self, status):
        if status < 0:
            self.__throwError(status)
        return status

    def __throwError(self, code):
        msg = create_string_buffer(1024)
        self.dll.TLSPCNT_errorMessage(self.devSession, c_int(code), msg)
        raise NameError(c_char_p(msg.raw).value)
    
    def conncect_to_first_device(self):
        self.findRsrc()
        print("Devices found: " + str(self.devCnt.value))
        
        RsrcName=self.getRsrcName()
        
        self.close()
        
        self.open(resourceName=self.resourceName)
        print('Opened device: %s'%str(RsrcName))
        

    def open(self, resourceName, IDQuery=c_bool(True), resetDevice=c_bool(True)):
        """
        This function initializes the instrument driver session and performs the following initialization actions:
        
        (1) Opens a session to the Default Resource Manager resource and a session to the specified device using the Resource Name.
        (2) Performs an identification query on the instrument.
        (3) Resets the instrument to a known state.
        (4) Sends initialization commands to the instrument.
        (5) Returns an instrument handle which is used to distinguish between different sessions of this instrument driver.
        
        Notes:
        (1) Each time this function is invoked a unique session is opened.  
        
        Args:
            resourceName (create_string_buffer)
            IDQuery (c_bool):This parameter specifies whether an identification query is performed during the initialization process.
            
            VI_OFF (0): Skip query.
            VI_ON  (1): Do query (default).
            
            resetDevice (c_bool):This parameter specifies whether the instrument is reset during the initialization process.
            
            VI_OFF (0) - no reset 
            VI_ON  (1) - instrument is reset (default)
            
        Returns:
            int: The return value, 0 is for success
        """
        
        self.dll.TLSPCNT_close(self.devSession)
        self.devSession.value = 0
        pInvokeResult = self.dll.TLSPCNT_init(resourceName, IDQuery, resetDevice, byref(self.devSession))
        self.__testForError(pInvokeResult)
        return pInvokeResult

    def close(self):
        """
        This function closes the instrument driver session.
        
        
        Returns:
            int: The return value, 0 is for success
        """
        pInvokeResult = self.dll.TLSPCNT_close(self.devSession)
        return pInvokeResult

    def _findRsrc(self, resourceCount):
        """
        This function finds all driver compatible devices attached to the PC and returns the number of found devices.
        
        Note:
        (1) The function additionally stores information like system name about the found resources internally. This information can be retrieved with further functions from the class, e.g. <Get Resource Description> and <Get Resource Information>.
        
        
        Args:
            resourceCount(c_uint32 use with byref) : The number of connected devices that are supported by this driver.
            
        Returns:
            int: The return value, 0 is for success
        """
        pInvokeResult = self.dll.TLSPCNT_findRsrc(self.devSession, resourceCount)
        self.__testForError(pInvokeResult)
        return pInvokeResult

    def findRsrc(self):
        self.devCnt = c_uint32()
        self._findRsrc(byref(self.devCnt))
        return self.devCnt.value
    
    def _getRsrcName(self, index, resourceName):
        """
        This function gets the resource name string needed to open a device with <Initialize>.
        
        Notes:
        (1) The data provided by this function was updated at the last call of <Find Resources>.
        
        Args:
            index(c_uint32) : This parameter accepts the index of the device to get the resource descriptor from.
            
            Notes: 
            (1) The index is zero based. The maximum index to be used here is one less than the number of devices found by the last call of <Find Resources>.
            
            resourceName(create_string_buffer(1024)) : This parameter returns the resource descriptor. Use this descriptor to specify the device in <Initialize>.
            
            Notes:
            (1) The array must contain at least TLSPCNT_BUFFER_SIZE (256) elements ViChar[256].
        Returns:
            int: The return value, 0 is for success
        """
        pInvokeResult = self.dll.TLSPCNT_getRsrcName(self.devSession, index, resourceName)
        self.__testForError(pInvokeResult)
        return pInvokeResult

    def getRsrcName(self,devInd=0):
        self.resourceName = create_string_buffer(1024)
        self._getRsrcName(c_int(devInd),self.resourceName)
        RsrcName = c_char_p(self.resourceName.raw).value.decode()
        return RsrcName

    def _getRsrcInfo(self, index, modelName, serialNumber, manufacturer, deviceAvailable):
        """
        This function gets information about a connected resource.
        
        Notes:
        (1) The data provided by this function was updated at the last call of <Find Resources>.
        
        Args:
            index(c_uint32) : This parameter accepts the index of the device to get the resource descriptor from.
            
            Notes: 
            (1) The index is zero based. The maximum index to be used here is one less than the number of devices found by the last call of <Find Resources>.
            
            modelName(create_string_buffer(1024)) : This parameter returns the model name of the device.
            
            Notes:
            (1) The array must contain at least TLSPCNT_BUFFER_SIZE (256) elements ViChar[256].
            (2) You may pass VI_NULL if you do not need this parameter.
            (3) Serial interfaces over Bluetooth will return the interface name instead of the device model name.
            serialNumber(create_string_buffer(1024)) : This parameter returns the serial number of the device.
            
            Notes:
            (1) The array must contain at least TLSPCNT_BUFFER_SIZE (256) elements ViChar[256].
            (2) You may pass VI_NULL if you do not need this parameter.
            (3) The serial number is not available for serial interfaces over Bluetooth.
            manufacturer(create_string_buffer(1024)) : This parameter returns the manufacturer name of the device.
            
            Notes:
            (1) The array must contain at least TLSPCNT_BUFFER_SIZE (256) elements ViChar[256].
            (2) You may pass VI_NULL if you do not need this parameter.
            (3) The manufacturer name is not available for serial interfaces over Bluetooth.
            deviceAvailable(c_int16 use with byref) : Returns the information if the device is available.
            Devices that are not available are used by other applications.
            
            Notes:
            (1) You may pass VI_NULL if you do not need this parameter.
            
        Returns:
            int: The return value, 0 is for success
        """
        pInvokeResult = self.dll.TLSPCNT_getRsrcInfo(self.devSession, index, modelName, serialNumber, manufacturer, deviceAvailable)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    
    def getRsrcInfo(self,devInd=0):
        self.modelName = create_string_buffer(1024)
        self.serialNumber = create_string_buffer(1024)
        self.manufacturer = create_string_buffer(1024)
        self.devAvailable = c_bool()
        self._getRsrcInfo(c_int16(devInd),self.modelName,self.serialNumber,self.manufacturer,byref(self.devAvailable))
        
        modelName = c_char_p(self.modelName.raw).value.decode()
        serialNumber = c_char_p(self.serialNumber.raw).value.decode()
        manufacturer = c_char_p(self.manufacturer.raw).value.decode()
        devAvailable = self.devAvailable.value
        
        return modelName,serialNumber,manufacturer,devAvailable
    
    
    def writeRegister(self, reg, value):
        pInvokeResult = self.dll.TLSPCNT_writeRegister(self.devSession, reg, value)
        self.__testForError(pInvokeResult)
        return pInvokeResult

    def readRegister(self, reg, value):
        pInvokeResult = self.dll.TLSPCNT_readRegister(self.devSession, reg, value)
        self.__testForError(pInvokeResult)
        return pInvokeResult

    def presetRegister(self):
        """
        This function presets all status registers to default.
        
        Returns:
            int: The return value, 0 is for success
        """
        pInvokeResult = self.dll.TLSPCNT_presetRegister(self.devSession)
        self.__testForError(pInvokeResult)
        return pInvokeResult

    def _setDispBrightness(self, val):
        """
        This function sets the display brightness.
        
        Args:
            val(c_double) : This parameter specifies the display brightness.
            
            Range   : 0.0 .. 1.0
            Default : 1.0
            
        Returns:
            int: The return value, 0 is for success
        """
        pInvokeResult = self.dll.TLSPCNT_setDisplayBrightness(self.devSession, val)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    
    def setDispBrightness(self,val=0.5):
        dispVal = c_double(val)
        self._setDispBrightness(dispVal)
                

    def _getDispBrightness(self, pVal):
        """
        This function returns the display brightness.
        
        
        Args:
            pVal(c_double use with byref) : This parameter returns the display brightness. Value range is 0.0 to 1.0.
        Returns:
            int: The return value, 0 is for success
        """
        pInvokeResult = self.dll.TLSPCNT_getDisplayBrightness(self.devSession, pVal)
        self.__testForError(pInvokeResult)
        return pInvokeResult

    def getDispBrightness(self):
        dispVal = c_double()
        self._getDispBrightness(byref(dispVal))
        return dispVal.value

    def errorMessage(self, statusCode, description):
        """
        This function takes the error code returned by the instrument driver functions interprets it and returns it as an user readable string. 
        
        Status/error codes and description:
        
        --- Instrument Driver Errors and Warnings ---
        Status      Description
        -------------------------------------------------
                 0  No error (the call was successful).
        0x3FFF0085  Unknown Status Code     - VI_WARN_UNKNOWN_STATUS
        0x3FFC0901  WARNING: Value overflow - VI_INSTR_WARN_OVERFLOW
        0x3FFC0902  WARNING: Value underrun - VI_INSTR_WARN_UNDERRUN
        0x3FFC0903  WARNING: Value is NaN   - VI_INSTR_WARN_NAN
        0xBFFC0001  Parameter 1 out of range. 
        0xBFFC0002  Parameter 2 out of range.
        0xBFFC0003  Parameter 3 out of range.
        0xBFFC0004  Parameter 4 out of range.
        0xBFFC0005  Parameter 5 out of range.
        0xBFFC0006  Parameter 6 out of range.
        0xBFFC0007  Parameter 7 out of range.
        0xBFFC0008  Parameter 8 out of range.
        0xBFFC0012  Error Interpreting instrument response.
        
        --- Instrument Errors --- 
        Range: 0xBFFC0700 .. 0xBFFC0CFF.
        Calculation: Device error code + 0xBFFC0900.
        Please see your device documentation for details.
        
        --- VISA Errors ---
        Please see your VISA documentation for details.
        
        
        Args:
            statusCode(ViStatus) : This parameter accepts the error codes returned from the instrument driver functions.
            
            Default Value: 0 - VI_SUCCESS
            description(create_string_buffer(1024)) : This parameter returns the interpreted code as an user readable message string.
            
            Notes:
            (1) The array must contain at least 512 elements ViChar[512].
            
        Returns:
            int: The return value, 0 is for success
        """
        pInvokeResult = self.dll.TLSPCNT_errorMessage(self.devSession, statusCode, description)
        self.__testForError(pInvokeResult)
        return pInvokeResult

    def reset(self):
        """
        This function resets the device.
        Returns:
            int: The return value, 0 is for success
        """
        pInvokeResult = self.dll.TLSPCNT_reset(self.devSession)
        self.__testForError(pInvokeResult)
        return pInvokeResult

    def _selfTest(self, selfTestResult, description):
        """
        This function runs the device self test routine and returns the test result.
        
        Args:
            selfTestResult(c_int16 use with byref) : This parameter contains the value returned from the device self test routine. A retured zero value indicates a successful run, a value other than zero indicates failure.
            description(create_string_buffer(1024)) : This parameter returns the interpreted code as an user readable message string.
            
            Notes:
            (1) The array must contain at least 256 elements ViChar[256].
            
        Returns:
            int: The return value, 0 is for success
        """
        pInvokeResult = self.dll.TLSPCNT_self_test(self.devSession, selfTestResult, description)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    
    def selfTest(self):
        testResult = c_int16()
        description = create_string_buffer(1024)
        self._selfTest(byref(testResult),description)
        return testResult.value, c_char_p(description.raw).value.decode()

    def _revisionQuery(self, instrumentDriverRevision, firmwareRevision):
        """
        This function returns the revision numbers of the instrument driver and the device firmware.
        
        Args:
            instrumentDriverRevision(create_string_buffer(1024)) : This parameter returns the Instrument Driver revision.
            
            Notes:
            (1) The array must contain at least 256 elements ViChar[256].
            (2) You may pass VI_NULL if you do not need this value.
            
            firmwareRevision(create_string_buffer(1024)) : This parameter returns the device firmware revision. 
            
            Notes:
            (1) The array must contain at least 256 elements ViChar[256].
            (2) You may pass VI_NULL if you do not need this value.
            
        Returns:
            int: The return value, 0 is for success
        """
        pInvokeResult = self.dll.TLSPCNT_revision_query(self.devSession, instrumentDriverRevision, firmwareRevision)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    
    def revisionQuery(self):
        instrumentDriverRevision = create_string_buffer(1024)
        firmwareRevision = create_string_buffer(1024)
        self._revisionQuery(instrumentDriverRevision, firmwareRevision)
        return c_char_p(instrumentDriverRevision.raw).value.decode(),c_char_p(firmwareRevision.raw).value.decode()
        
        
    def _identificationQuery(self, manufacturerName, deviceName, serialNumber):
        """
        This function returns the device identification information.
        
        Args:
            manufacturerName(create_string_buffer(1024)) : This parameter returns the manufacturer name.
            
            Notes:
            (1) The array must contain at least 256 elements ViChar[256].
            (2) You may pass VI_NULL if you do not need this value.
            
            deviceName(create_string_buffer(1024)) : This parameter returns the device name.
            
            Notes:
            (1) The array must contain at least 256 elements ViChar[256].
            (2) You may pass VI_NULL if you do not need this value.
            
            serialNumber(create_string_buffer(1024)) : This parameter returns the device serial number.
            
            Notes:
            (1) The array must contain at least 256 elements ViChar[256].
            (2) You may pass VI_NULL if you do not need this value.
            
            firmwareRevision(create_string_buffer(1024)) : This parameter returns the device firmware revision.
            
            Notes:
            (1) The array must contain at least 256 elements ViChar[256].
            (2) You may pass VI_NULL if you do not need this value.
            
        Returns:
            int: The return value, 0 is for success
        """
        pInvokeResult = self.dll.TLSPCNT_identification_query(self.devSession, manufacturerName, deviceName, serialNumber)
        self.__testForError(pInvokeResult)
        return pInvokeResult

    def identificationQuery(self):
        manufacturerName, deviceName, serialNumber = create_string_buffer(1024),create_string_buffer(1024), create_string_buffer(1024)
        self._identificationQuery(manufacturerName, deviceName, serialNumber)
        return c_char_p(manufacturerName.raw).value.decode(),c_char_p(deviceName.raw).value.decode(),c_char_p(serialNumber.raw).value.decode()
    

    def _getCalibrationMessage(self,msg):
        pInvokeResult = self.dll.TLSPCNT_getCalibrationMessage(self.devSession,msg)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    
    def getCalibrationMessage(self):
        msg = create_string_buffer(1024)
        self._getCalibrationMessage(msg)
        return c_char_p(msg.raw).value.decode()
    
    def startZeroing(self):
        pInvokeResult = self.dll.TLSPCNT_startZeroing(self.devSession)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    
    def abortZeroing(self):
        pInvokeResult = self.dll.TLSPCNT_abortZeroing(self.devSession)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    
    def _getZeroState(self,state):
        pInvokeResult = self.dll.TLSPCNT_getZeroState(self.devSession,state)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    
    def getZeroState(self):
        state = c_bool()
        self._getZeroState(byref(state))
        return state.value
    
    def _setZeroValue(self,val):
        pInvokeResult = self.dll.TLSPCNT_setZeroValue(self.devSession,val)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    
    def setZeroValue(self,value):
        val = c_double(value)
        self._setZeroValue(val)
        
    def _getZeroValue(self,val):
        pInvokeResult = self.dll.TLSPCNT_getZeroValue(self.devSession,val)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    def getZeroValue(self):
        val = c_double()
        self._getZeroValue(byref(val))
        return val.value
    
    def _getFrequencyCountThreshold(self,val):
        pInvokeResult = self.dll.TLSPCNT_getFrequencyCountThreshold(self.devSession,val)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    
    def getFrequencyCountThreshold(self):
        val = c_uint16()
        self._getFrequencyCountThreshold(byref(val))
        return val.value
    
    def _setFrequencyCountThreshold(self,val):
        pInvokeResult = self.dll.TLSPCNT_setFrequencyCountThreshold(self.devSession,val)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    
    def setFrequencyCountThreshold(self,value):
        val = c_uint16(value)
        self._setFrequencyCountThreshold(val)
        
    def startFrequencyCounting(self):
        pInvokeResult = self.dll.TLSPCNT_startFrequencyCounting(self.devSession)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    
    def stopFrequencyCounting(self):
        pInvokeResult = self.dll.TLSPCNT_stopFrequencyCounting(self.devSession)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    
    def _getFrequencyCountingState(self,val):
        pInvokeResult = self.dll.TLSPCNT_getFrequencyCountingState(self.devSession,val)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    def getFrequencyCountingState(self):
        val = c_bool()
        self._getFrequencyCountingState(byref(val))
        return val.value
    
    def _setArrayLength(self,val):
        pInvokeResult = self.dll.TLSPCNT_setArrayLenght(self.devSession,val)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    
    def setArrayLength(self,value):
        val = c_uint32(value)
        self._setArrayLength(val)
        
    def _getArrayLength(self,val):
        pInvokeResult = self.dll.TLSPCNT_getArrayLenght(self.devSession,val)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    
    def getArrayLength(self):
        val = c_uint32()
        self._getArrayLength(byref(val))
        return val.value
    
    def _setBinWidth(self,val):
        pInvokeResult = self.dll.TLSPCNT_setBinWidth(self.devSession,val)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    
    def setBinWidth(self,value):
        val = c_uint32(value)
        self._setBinWidth(val)
        return val.value
    
    def _getBinWidth(self,val):
        pInvokeResult = self.dll.TLSPCNT_getBinWidth(self.devSession,val)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    
    def getBinWidth(self):
        val = c_uint32()
        self._setBinWidth(byref(val))
        return val.value
    
    def _setDeadTime(self,val):
        pInvokeResult = self.dll.TLSPCNT_setDeadTime(self.devSession,val)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    
    def setDeadTime(self,value):
        val = c_uint32(value)
        self._setDeadTime(val)
    
    def _getDeadTime(self,val):
        pInvokeResult = self.dll.TLSPCNT_getDeadtime(self.devSession,val)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    
    def getDeadTime(self):
        val = c_uint32()
        self._getDeadTime(byref(val))
        return val.value
    
    def _setAverageCount(self,val):
        pInvokeResult = self.dll.TLSPCNT_setAverageCount(self.devSession,val)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    
    def setAverageCount(self,value):
        val = c_uint16(value)
        self._setAverageCount(val)
        
    def _getAverageCount(self,val):
        pInvokeResult = self.dll.TLSPCNT_getAverageCount(self.devSession,val)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    
    def getAverageCount(self):
        val = c_uint16()
        self._getAverageCount(byref(val))
        return val.value
    
    def resetStatistics(self):
        pInvokeResult = self.dll.TLSPCNT_resetStatistics(self.devSession)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    
    def _getFrequency(self,freq,fmin,fmax,favg):
        pInvokeResult = self.dll.TLSPCNT_getFrequency(self.devSession,freq,fmin,fmax,favg)
        self.__testForError(pInvokeResult)
        return pInvokeResult

    def getFrequency(self,return_all=False):
        freq,fmin,fmax,favg = c_double(),c_double(),c_double(),c_double()
        self._getFrequency(byref(freq), byref(fmin),byref(fmax),byref(favg))
        if return_all:
            return freq.value, fmin.value, fmax.value, favg.value
        else:
            return freq.value
        
    def _getCount(self,val):
        pInvokeResult = self.dll.TLSPCNT_getCount(self.devSession,val)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    
    def getCount(self):
        val = c_int32()
        self._getCount(byref(val))
        return val.value
    
    def _getTime(self,val):
        pInvokeResult = self.dll.TLSPCNT_getTime(self.devSession,val)
        self.__testForError(pInvokeResult)
        return pInvokeResult
    
    def getTime(self):
        val = c_double()
        self._getTime(byref(val))
        return val.value
    
    # def _getBins(self,bins,blen):
    #     pInvokeResult = self.dll.TLSPCNT_getBins(self.devSession,bins,blen)
    #     self.__testForError(pInvokeResult)
    #     return pInvokeResult
    
    # def getBins(self):
    #     bins,blen = c_int32(), c_uint32()
    #     self._getBins(byref(bins),byref(blen))
    #     return bins.value, blen.value
