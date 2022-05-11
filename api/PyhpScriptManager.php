<?php

namespace App\api;

class PyhpScriptManager {

    protected $runningId;
    protected $scriptName;
    protected $isRunning;

    public function __construct($scriptName, $runningId) {
        $this->scriptName = $scriptName;
        $this->runningId  = $runningId;
        $this->isRunning  = false;
    }

    private function getStatusPath() {
        return PyhpScriptController::$STATUS_PATH . $this->runningId . ".status.json";
    }

    private function getDataPath() {
        return PyhpScriptController::$DATA_PATH . $this->runningId . ".data.json";
    }

    private function openSafeFile($path, $maxTry, $waitDelay) {
        $handler  = false;
        $tryCount = 0;

        if (file_exists($this->getStatusPath()))
            $handler = file_get_contents($path);

        while ($handler == false) {
            if (file_exists($path))
                $handler = file_get_contents($path);

            $tryCount ++;
            sleep($waitDelay);
            if ($tryCount > $maxTry)
                return false;
        }

        return $handler;
    }

    /**
     * Update the running status of the script
     * Return false if it can't read the status file, true if he can
     *
     * @param $maxTry
     * @param $waitDelay
     * @return bool
     */

    public function updateStatus($maxTry = 10, $waitDelay = 1) {
        $result = $this->openSafeFile($this->getStatusPath(), $maxTry, $waitDelay);

        if (!$result) return false;

        $data = json_decode($result);
        $this->isRunning = $data->isRunning;

        return true;
    }

    /**
     * try to access to the data of the script
     * Return the data if he can, else he return false
     * @param $maxTry
     * @param $waitDelay
     * @return false|mixed
     */

    public function getData($maxTry = 10, $waitDelay = 1) {
        $result = $this->openSafeFile($this->getDataPath(), $maxTry, $waitDelay);

        if (!$result) return false;

        return json_encode($result);
    }

    /**
     * Will destroy the data and status file
     * Use it when you are done with handling the data
     *
     * @return void
     */


    public function destroyScriptData() {
        unlink($this->getDataPath());
        unlink($this->getStatusPath());
    }

    /**
     * Return the status of the python script
     * Should be call after updateStatus function
     *
     * @return bool
     */

    public function isRunning(): bool {
        return $this->isRunning;
    }
}

