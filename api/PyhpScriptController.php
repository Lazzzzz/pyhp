<?php

namespace App\api;

use Livewire\Component;

class PyhpScriptController {

    public static $DIRECTORY_PATH;
    public static $DATA_PATH;
    public static $STATUS_PATH;
    public static $SCRIPTS_PATH;
    public static $QUEUE_PATH;

    /**
     * Put the init function inside the route "web.php"
     */

    public static function init() {
        self::$DIRECTORY_PATH = base_path()         . '/python/';
        self::$DATA_PATH = self::$DIRECTORY_PATH    . 'data/';
        self::$STATUS_PATH = self::$DIRECTORY_PATH  . 'status/';
        self::$SCRIPTS_PATH = self::$DIRECTORY_PATH . 'scripts/';
        self::$QUEUE_PATH = self::$DIRECTORY_PATH   . 'queue/';
    }

    /**
     * Start a script and return the instance id
     * @return PyhpScriptManager | bool <p>Return the scripts' manager if the script succeed to start, false if not</p>
     */

    public static function startScript($name, $args = []) {
        $scriptId   = time();
        $script     = new PyhpScriptManager($name, $scriptId);

        $scriptPath = self::$QUEUE_PATH . $scriptId . '.json';

        $data = [
            'name' => $name,
            'args' => $args
        ];

        $json = json_encode($data, JSON_PRETTY_PRINT);

        if (file_put_contents($scriptPath, $json)) {
            $script->updateStatus();
            return $script;
        }

        return false;
    }

    /**
     * Return a new instance of a script manager by id
     *      *
     * @param $name
     * @param $id
     * @return PyhpScriptManager
     */

    public static function getScriptFromId($name, $scriptId) {
        return new PyhpScriptManager($name, $scriptId);
    }
}
