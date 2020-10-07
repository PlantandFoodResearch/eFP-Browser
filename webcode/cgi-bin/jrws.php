<?php

/*
 * :: PHP File Library ::
 * The File class provides a collection of functions, designed to be used statically, to assist
 * you with some basic filesystem operations. Support is provided for PHP4
 *
 * :: Functions ::
 * read   : completely read a file to a string (same as file_get_contents in PHP 5)
 * write  : write a string to a file (same as file_put_contents in PHP5)
 * append : append a string to a file (same as file_put_contents in PHP5)
 * remove : delete a file, directory or link from the filesystem. WARNING: recursive. Use with care.
 * 
 * :: Copyright ::
 * Copyright (c) 2009-2010 Julian Tonti-Filippini (julian.tonti@gmail.com)
 *
 * :: License ::
 * Creative Commons BY-3.0, http://creativecommons.org/licenses/by/3.0/
 *
 * :: Disclaimer ::
 * The author accepts no liability for system damage resulting from use of this code. It is open source
 * so do your own due-diligence and do not use this code if you do not approve of it. The author also 
 * accepts no responsibility for consequences resulting from the use of code that has been modified 
 * from the original source.
 *
 * :: Version Log ::
 * 2009-Mar-28: First release (alpha: please report bugs to the author)
 */
class File
{
	//Read from a file
	function read($f)
	{
		$path = realpath($f);
		if (!$path) throw new Exception("Error: invalid path: $f");
		if (!is_file($path)) throw new Exception("Error: file not found: $f");
		if (!is_readable($path)) throw new Exception("Error: file not readable: $f");
		
		//file_get_contents is not backwards compatible with PHP4, so we do it the old way
		$fp = fopen($path, 'r');
		$str = '';
		
		while (!feof($fp))
		{
			$str .= fgets($fp);
		}
		fclose($fp);
		return $str;
	}
	
	//Write to a file
	function write($f, $str)
	{
		$path = realpath($f);
		touch($path);
		if (!$path) throw new Exception("Error: invalid path: $f");
		if (!is_file($path)) throw new Exception("Error: file could not be created: $f");
		if (!is_writable($path)) throw new Exception("Error: file not writable: $f");
		
		//file_put_contents is not backwards compatible with PHP4, so we do it the old way
		$fp = fopen($path, 'w');
		fputs($fp,$str);
		fclose($fp);
		return;
	}
	
	//Append to a file
	function append($f, $str)
	{
		$path = realpath($f);
		touch($path);
		if (!$path) throw new Exception("Error: invalid path: $f");
		if (!is_file($path)) throw new Exception("Error: file could not be created: $f");
		if (!is_writable($path)) throw new Exception("Error: file not writable: $f");
		
		//file_put_contents is not backwards compatible with PHP4, so we do it the old way
		$fp = fopen($path, 'a');
		fputs($fp,$str);
		fclose($fp);
		return;
	}
	
	//Remove a file, link or directory. Directory removal is recursive so USE WITH CAUTION
	function rm($el)
	{
		//Very important!
		if (basename($el) == '..' || basename($el) == '.') return;
		
		if (is_file($el) || is_link($el))
		{
			echo "rm: $el\n";
			if (!unlink($el)) throw new Exception("Error: unable to remove file due to inadequate permission: $el");
			return;
		}
		else if (is_dir($el))
		{
			$files = scandir($el);
			var_dump($files);
		
			foreach ($files as $file)
			{
				//Secondary backup of first line
				if ($file == '.' || $file == '..') continue;
				File::rm("$el/$file");
			}
			echo "rmdir: $el\n";
			rmdir($el);
		}
		else
		{
			return;
		}
	}
}

/*
 * :: PHP JSON Library ::
 * The JSON class provides a collection of functions, designed to be used statically, to assist
 * you with JSON operations. At this stage the source does not support versions of PHP earlier 
 * than 5.2 however this will be addressed in future releases.
 *
 * :: Dependencies ::
 * - PHP 5.2.0 or above
 * - PHP support for cURL (compiled --with-curl=[DIR])
 * - file.php
 *
 * :: Functions ::
 * encode   : convert an item into a JSON string equivalent
 * decode   : convert a JSON string into an equivalent item
 * save     : save an item to a file as a JSON string
 * load     : load a JSON string from a file to an item
 * download : download a JSON string from a remote site and build to an item
 * text     : print a JSON string in human readable format (minus strict grammar)
 * html     : print a JSON string in stylized HTML
 * approve  : check an object against a template to ensure structural correctness
 * apply    : left join a template onto an existing object skipping collisions
 * override : left join a template onto an existing object replacing collisions
 * clean    : remove all object properties that do not exist in a specified template
 * 
 * :: Copyright ::
 * Copyright (c) 2009-2010 Julian Tonti-Filippini (julian.tonti@gmail.com)
 *
 * :: License ::
 * Creative Commons BY-3.0, http://creativecommons.org/licenses/by/3.0/
 *
 * :: Disclaimer ::
 * The author accepts no liability for system damage resulting from use of this code. It is open source
 * so do your own due-diligence and do not use this code if you do not approve of it. The author also 
 * accepts no responsibility for consequences resulting from the use of code that has been modified 
 * from the original source.
 *
 * :: Version Log ::
 * 2009-Mar-28: First release (alpha: please report bugs to the author)
 */
//Class for managing JSON-based operations (PHP >= 5.2 and libcurl required)
class JSON
{
	//Encode an object as JSON
	function encode($d)
	{
		//TODO: backwards compatibility for PHP4
		if (!function_exists('json_encode'))
		{
			throw new Exception("Your version of PHP does not support json_encode (>5.2 required)");
		}
		$str = json_encode($d);
		
		if (!$str)
		{
			throw new Exception("Error: json_encode failed.");
		}
		return $str;
	}
	
	//Decode a string to a JSON object
	function decode($str, $assoc=true)
	{
		//TODO: backwards compatibility for PHP4
		if (!function_exists('json_decode'))
		{
			throw new Exception("Your version of PHP does not support json_encode (>5.2 required)");
		}
		$str = trim($str);
		
		if (!$str)
		{
			return null;
		}
		$obj = json_decode($str, $assoc);
		
		if ($obj === null)
		{
			throw new Exception("Illegally formed JSON string: json_decode failed. The string was $str");
		}
		return $obj;
	}
	
	//Save data to disk in JSON format
	function save($data, $file)
	{
		File::write($file, JSON::encode($data));
	}
	
	//Load a JSON object from a file
	function load($file,$as_array=true)
	{
		return JSON::decode(File::read($file), $as_array);
	}
	
	//Load a JSON object from an HTTP address
	function download($url,$as_array=true)
	{
		$curl = curl_init();
		curl_setopt($curl, CURLOPT_URL, $url);
		curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
		curl_setopt($curl, CURLOPT_FOLLOWLOCATION, true);
		curl_setopt($curl, CURLOPT_HTTPHEADER, array(
			'Accept: text/html,application/xhtml+xml,application/xml',
			'Accept-Language: en-us,en',
			'Accept-Charset: ISO-8859-1,utf-8',
			'Keep-Alive: 300',
			'Connection: keep-alive'
		));
		$response = curl_exec($curl);
		
		if (curl_errno($curl))
		{
			throw new Exception('URL transaction error: ' . curl_error($curl));
		}
		curl_close($curl);
		
		return JSON::decode($response, $as_array);
	}
	
	//Print a JSON object as human-readable plain text
	function text($obj,$level=0)
	{
		$s = "{\n";
		$level++;
		
		foreach($obj as $k => $v)
		{
			$s .= str_repeat("    ",$level) . "$k : " . (is_array($v) ? JSON::text($v,$level) : $v) . "\n";
		}
		return $s . str_repeat("    ",$level-1) . "}";
	}
	
	//Print a JSON object as human-readable HTML
	function html($obj,$level=0)
	{
		$s = "<span style='color:red'>{</span></div>\n";
		$level++;
		
		foreach($obj as $k => $v)
		{
			if (is_object($v) || is_array($v))
			{
				$s .= "<div style='padding-left:" . (20*$level) . "px'><span style='color:orange'>$k</span> : " . JSON::html($v,$level) . "</div>\n";
			}
			else if (is_numeric($v))
			{
				$s .= "<div style='padding-left:" . (20*$level) . "px'><span style='color:blue'>$k</span> : <span style='color:blue'>$v</span></div>\n";
			}
			else if (is_bool($v))
			{
				$s .= "<div style='padding-left:" . (20*$level) . "px'><span style='color:magenta'>$k</span> : <span style='color:magenta'>" . ($v ? 'true' : 'false') . "</span></div>\n";
			}
			else if (is_null($v))
			{
				$s .= "<div style='padding-left:" . (20*$level) . "px'><span style='color:orange'>$k</span> : <span style='color:orange'>null</span></div>\n";
			}
			else
			{
				$s .= "<div style='padding-left:" . (20*$level) . "px'><span style='color:green'>$k</span> : <span style='color:green'>$v</span></div>\n";
			}
		}
		return $s . "<div style='padding-left:" . (20*($level-1)) . "px'><span style='color:red'>}</span>";
	}
	
	//Validate the structure of a target object against a template
	function approve(&$target, &$template)
	{
		if (!is_array($template)) throw new Exception("Error: JSON::validate expects the second parameter to be an array");
		
		foreach ($template as $k => $v)
		{
			if (!isset($target[$k]))
			{
				echo "JSON::validate failed: source['$k'] is missing\n";
				return false;
			}
			if (is_array($v))
			{
				if (!JSON::validate($target[$k], $v)) return false;
			}
		}
		return true;
	}
	
	//Inspired by Ext.apply
	function apply(&$target, &$template, $force=false)
	{
		foreach ($template as $k => $v)
		{
			#echo(sprintf("k=%s<br>v=%s<br>", $k, $v));
			if (!isset($target[$k]))
			{
				$target[$k] = $v;
			}
			else if (is_array($v))
			{
				JSON::apply($target[$k], $v, $force);
			}
			else
			{
				if ($force) $target[$k] = $v;
			}
		}
	}
	
	//Forcefully override target params with the template params
	function override(&$target, &$template)
	{
		JSON::apply($target,$template,true);
	}
	
	//Clean a source object against a template
	function clean(&$target, &$template)
	{
		foreach ($target as $k => $v)
		{
			if (!isset($template[$k]))
			{
				unset($target[$k]);
			}
			else if (is_array($v))
			{
				JSON::clean($v, $template[$k]);
			}
		}
	}
}

/*
 * :: PHP JRWS Library ::
 * This file contains a collection of classes that enable you to make use of JSON / REST Web Services.
 * Typically, the way to proceed is to first create a JDF as a stand-alone file, then to include this
 * library in your script and point it to the URL of the JDF you created. A call to validiate will 
 * automatically process the $_REQUEST super-global. For example:
 *
 * <?php
 *    require_once 'jrws.php';
 *    JRWS::validate('http://www.path.to/your/file.jdf');
 *    JRWS::respond('It all worked');
 * ?>
 *
 * :: Classes ::
 * JRWS          : designed to be used statically to drive JRWS validation
 * JRWS_Factory  : generates JRWS Types on command
 * JRWS_Typedef  : base class for JRWS Types
 * JRWS_Null     : a null type
 * JRWS_Boolean  : a boolean type
 * JRWS_Integer  : an integer type
 * JRWS_Real     : a floating point type
 * JRWS_String   : a string type
 * JRWS_Map      : a dictionary / hashtable / object type
 * JRWS_Array    : a mono-typed array type
 * JRWS_Tuple    : a tuple type
 * JRWS_Function : a function type
 * JDF_Node      : class to represent a JRWS Description File as a sub-node in a JDF graph
 * JDF_Root      : the root node (primary JDF) in a JDF graph
 * 
 * :: Copyright ::
 * Copyright (c) 2009-2010 Julian Tonti-Filippini (julian.tonti@gmail.com)
 *
 * :: License ::
 * Creative Commons BY-3.0, http://creativecommons.org/licenses/by/3.0/
 *
 * :: Disclaimer ::
 * The author accepts no liability for system damage resulting from use of this code. It is open source
 * so do your own due-diligence and do not use this code if you do not approve of it. The author also 
 * accepts no responsibility for consequences resulting from the use of code that has been modified 
 * from the original source.
 *
 * :: Version Log ::
 * 2009-Mar-28: First release (alpha: please report bugs to the author)
 */
//Base JRWS class
class JRWS
{
	/* 
	 * Automatically validate a request coming from a client against the specified JDF
	 * Produces HTTP errors and aborts execution when a problem is found
	 */
	function validate($url)
	{
		return JRWS::validate_from_url($url);
	}
	function validate_from_url($url)
	{
		###$test = JRWS::validate_from_object(JSON::download($url));
		###echo(sprintf("test=%s<br>",$test));
		return JRWS::validate_from_object(JSON::download($url));
	}
	function validate_from_file($file)
	{
		return JRWS::validate_from_object(JSON::load($file));
	}
	function validate_from_string($json)
	{
		return JRWS::validate_from_object(JSON::decode($json));
	}
	function validate_from_object($data)
	{
		//Build the JDF
		$jdf = new JDF_Root();
		$jdf->build_from_object($data);
		## HN TESTING
		##echo(print_r($data['readme'], true));
		//JRWS::error(520, "Server: the JDF for this service could not be loaded from address $url");
		
		if (count($_GET) == 0 && count($_POST) == 0)
		{
			die($jdf->dump_json());
		}
		if (isset($_REQUEST['text']))
		{
			die($jdf->dump_text());
		}
		if (isset($_REQUEST['json']))
		{
			die($jdf->dump_json());
		}
		if (isset($_REQUEST['html']))
		{
			die($jdf->dump_html());
		}
		if (!isset($_REQUEST['request']))
		{
			JRWS::error(420, "Bad Input: no 'request' parameter was found in the input data");
		}
		$function = isset($_REQUEST['function']) ? $_REQUEST['function'] : '';
		##$test = $_REQUEST['function'];
		##echo(sprintf("test=%s<br>",$test));
		$request  = JSON::decode($_REQUEST['request']);
		## HN: Testing
		##JRWS::error("request", print_r(JSON::decode($_REQUEST['request'], true)));
		##echo(print_r($request['dna'], true));
		##echo("validating jdf:<br>");
		##echo(sprintf("function=%s<br>",$function));
		##$return_val= $jdf->validate($function, $request);
		##echo(sprintf("return_val from validate=%s<br>",$return_val));
		
		return $jdf->validate($function, $request);
	}
	
	function error($code, $message)
	{
		header("HTTP/1.1 $code $message");
		echo "Error $code $message";
		exit();
	}
	
	//Respond to a client with JSON
	function respond($data)
	{
		header("HTTP/1.1 200 OK");
		echo JSON::encode($data);
		#exit();
	}
}

//JRWS type factory
class JRWS_Factory
{
	function generate(&$definition, &$scope)
	{
		if (!is_array($definition))
		{
			throw new Exception("Illegal definition passed to JRWS_Typedef constructor. Definition must be an array.");
		}
		if      (isset($definition['bool']))     $def = new JRWS_Boolean($definition['bool'], $scope);
		else if (isset($definition['int']))      $def = new JRWS_Integer($definition['int'], $scope);
		else if (isset($definition['real']))     $def = new JRWS_Real($definition['read'], $scope);
		else if (isset($definition['string']))   $def = new JRWS_String($definition['string'], $scope);
			#echo("testing def for String<br>");
			#echo(print_r($def, true));
			##$test=$def->def['regex'];
			##echo("<br>testing<br>");
			##echo(sprintf("regex=%s",$test));
			#echo(print_r($test, true));
			##echo("<br>");
			#$test = $def['regex'];
			#if (isset($this->['regex']))
			#{
			#	$test=$def['regex'];
			#	echo("testing<br>");
			#	echo(print_r($test, true));
			#}
			#else{
			#	echo("regex not defined<br>");
			#}
			#echo(print_r($def, true));
			#echo("<br>");
		else if (isset($definition['tuple']))    $def = new JRWS_Tuple($definition['tuple'], $scope);
		else if (isset($definition['array']))    $def = new JRWS_Array($definition['array'], $scope);
		else if (isset($definition['map']))      $def = new JRWS_Map($definition['map'], $scope);
		else if (isset($definition['function'])) $def = new JRWS_Function($definition['function'], $scope);
		else 
		{
			var_dump($definition);
			throw new Exception("Illegal definition passed to JRWS_Typedef constructor. Definition must be one of type bool|int|real|string|tuple|array|map|function");
		}
		#echo $def->def;
		return $def;
	}
}

//JRWS base type
class JRWS_TypeDef
{
	var $def;
	var $scope;
	
	function JRWS_TypeDef($definition, &$scope, $default)
	{
		if (!is_array($definition))
		{
			throw new Exception("The definition passed to a JRWS Type Object must be an array");
		}
		if (!is_array($default))
		{
			throw new Exception("The default passed to a JRWS Type Object must be an array");
		}
		JSON::apply($definition, $default);
		##$class_of_this = get_class($this);
		##echo(sprintf("class=%s<br>",$class_of_this));
		$this->def = $definition;
		$this->scope = $scope;
		#echo("def and scope have been defined<br>");
	}
	
	//Validate some data against this typedef (returns a bool to indicate success)
	function validate(&$data, &$type)
	{
		//Implement in the subclass
	}
}

//JRWS null type
class JRWS_Null extends JRWS_TypeDef
{
	function JRWS_Boolean($definition, &$scope)
	{
		parent::JRWS_TypeDef($definition, $scope, array());
	}
	function validate(&$data)
	{
		return $data == null;
	}
}

//JRWS boolean type
class JRWS_Boolean extends JRWS_TypeDef
{
	function JRWS_Boolean($definition, &$scope)
	{
		parent::JRWS_TypeDef($definition, $scope, array(
			'default' => true
		));
	}
	
	function validate(&$data)
	{
		return is_bool($data);
	}
}

//JRWS integer type
class JRWS_Integer extends JRWS_TypeDef
{
	function JRWS_Integer($definition, &$scope)
	{
		parent::JRWS_TypeDef($definition, $scope, array(
			'min' => null,
			'max' => null,
			'step' => 1,
			'regex' => '',
			'default' => 0
		));
	
	}
	function validate(&$data)
	{
		if (!is_int($data)) return false;
		if ($this->def['min'] !== null && $data < $this->def['min']) return false;
		if ($this->def['max'] !== null && $data > $this->def['max']) return false;
		if ($this->def['regex'] && ereg($this->def['regex'], $data) === false) return false;
		return true;
	}
}

//JRWS real type
class JRWS_Real extends JRWS_TypeDef
{
	function JRWS_Real($definition, &$scope)
	{
		parent::JRWS_TypeDef($definition, $scope, array(
			'min' => null,
			'max' => null,
			'regex' => '',
			'default' => 0.0
		));
	}
	function validate(&$data)
	{
		if (!is_float($data)) return false;
		if ($this->def['min'] !== null && $data < $jdf['min']) return false;
		if ($this->def['max'] !== null && $data > $jdf['max']) return false;
		if ($this->def['regex'] && ereg($this->def['regex'],$data) === false) return false;
		return true;
	}
}

//JRWS string type
class JRWS_String extends JRWS_TypeDef
{
	function JRWS_String($definition, &$scope)
	{
		parent::JRWS_TypeDef($definition, $scope, array(
			'regex' => '',
			'default' => ''
		));
		##echo("testing in JRWS_String<br>");
		##echo(print_r($this, true));
		##echo("<br><br>");
	}
	function validate(&$data)
	{
		###echo("validating in JRWS_String<br>");
		##echo(sprintf("data[agi]=%s",$data['agi']));
		##echo("<br>");
		###echo("data in JRWS_String validate=");
		###echo(print_r($data,true));
		###echo("<br>");
		###echo("checking this object in JRWS_String:");
		###echo(print_r($this, true));
		###echo("<br>");
		$keys = array_values($data);
		$key = $keys[0];
		###echo(sprintf("key = %s<br>", $key));

		if (!$this->def['regex'])
		{	
			###echo("regex does not exist<br>");
			return true;
		}
		###$result = eregi($this->def['regex'], $data['agi']);
		###if ($result == true)
		###{
		###	echo(sprintf("result from JRWS_String validation=%s<br>",$result));
		###}
		return eregi($this->def['regex'], $key);
	}
}

//JRWS map type
class JRWS_Map extends JRWS_TypeDef
{
	function JRWS_Map($definition, &$scope)
	{
		parent::JRWS_TypeDef($definition, $scope, array(
			'nullable' => true,
			'elements' => null
		));
	}
	function validate(&$data)
	{
		if (!$this->def['nullable'] && $data == null) return false;
		if (!is_array($data)) return false;
		
		//Validate existing object keys
		foreach ($data as $name => $value)
		{
			if (!isset($this->def['elements'][$name]))
			{
				return false;
			}
			if (!$this->scope->validate($value, $this->def['elements'][$name]))
			{
				return false;
			}
		}
		
		//Bomb if the spec demands object keys that the target does not have
		foreach ($this->def['elements'] as $name => $value)
		{
			if (!isset($data[$name]))
			{
				return false;
			}
		}
		return true;
	}
}

//JRWS array type
class JRWS_Array extends JRWS_TypeDef
{
	function JRWS_Array($definition, &$scope)
	{
		parent::JRWS_TypeDef($definition, $scope, array(
			'min' => null,
			'max' => null,
			'type' => null
		));
	}
	function validate(&$data)
	{
		if (!is_array($data)) return false;
		$size = count($data);
		if ($this->def['min'] !== null && $size < $this->def['min']) return false;
		if ($this->def['max'] !== null && $size > $this->def['max']) return false;
		
		//Validate existing object keys
		foreach ($data as $item)
		{
			if (!$this->scope->validate($item, $this->def['type']))
			{
				return false;
			}
		}
		return true;
	}
}

//JRWS tuple type
class JRWS_Tuple extends JRWS_TypeDef
{
	function JRWS_Tuple($definition, &$scope)
	{
		parent::JRWS_TypeDef($definition, $scope, array(
			'elements' => null
		));
		
		# Throw exception if definition is bad
		if ($this->def['elements'] != null && !is_array($this->def['elements']))
		{
			throw new Exception('Illegal definition provided to JRWS_Tuple constructor');
		}
	}
	function validate(&$data)
	{
		if ($data == null && $this->def['elements'] != null) return false;
		if ($data != null && $this->def['elements'] == null) return false;
		if (!is_array($data)) return false;
		
		$sizeData = count($data);
		$sizeDef = count($this->def['elements']);
		
		if ($sizeData != $sizeDef) return false;
		if ($sizeData == 0) return true;
		
		for ($i=0; $i<$sizeData; $i++)
		{
			$result = $this->scope->validate($data[$i], $this->def['elements'][$i]);
			
			if (!$result['success'])
			{
				return $result;
			}
		}
		return true;
	}
}

//JRWS function type
class JRWS_Function extends JRWS_TypeDef
{
	function JRWS_Function($definition, &$scope)
	{
		parent::JRWS_TypeDef($definition, $scope, array(
			'comment' => '',
			'request' => null,
			'response' => null,
			'throws' => null
		));
	}
	function validate(&$data)
	{
		###echo("validating in JRWS_Function<br>");
		##echo("request in JRWS_Function:");
		##echo(print_r($this->def['request'], true));
		##echo("<br>");
		##$class_of_this = get_class($this);
		##echo(sprintf("class=%s<br>",$class_of_this));
		###$result = $this->scope->validate($data, $this->def['request']);
		###if ($result == false)
		###{
		###	echo("result of JRWS_Function validation is false<br>");
		###}
		return $this->scope->validate($data, $this->def['request']);
	}
}

//A JDF is a node in the validation build-graph
class JDF_Node
{
	var $root;
	var $aliases;
	var $dictionary;
	var $functions;
	var $original;
	
	function JDF_Node(&$root, $jdf)
	{
		$this->root = &$root;
		$this->aliases    = array();
		$this->dictionary = array();
		$this->functions  = array();
		$this->original   = $jdf;
		
		//Build the JDF
		$default = array(
			'include' => array(),
			'define' => array(),
			'readme' => array(),
			'api' => array()
		);
		JSON::apply($this->original, $default);
		
		//Build the includes
		$this->aliases = $this->original['include'];
		
		foreach ($this->aliases as $alias => $url)
		{
			$this->import($alias, $url);
		}
		
		//Build the definitions
		$this->dictionary = $this->original['define'];
		
		foreach ($this->dictionary as $name => $definition)
		{
			##$class_of_this = get_class($this);
			##echo(sprintf("in JDF_Node, class=%s<br>",$class_of_this));
			##echo(sprintf("name=%s<br>",$name));
			$this->assign($this->dictionary[$name]);
		}
		
		//Add the basic types to the JDF's dictionary (these cannot be overridden)
		$def = array();
		
		$this->dictionary['int']      = new JRWS_Integer($def, $this);
		$this->dictionary['real']     = new JRWS_Real($def, $this);
		$this->dictionary['bool']     = new JRWS_Boolean($def, $this);
		$this->dictionary['string']   = new JRWS_String($def, $this);
		$this->dictionary['object']   = new JRWS_Map($def, $this);
		$this->dictionary['array']    = new JRWS_Array($def, $this);
		$this->dictionary['tuple']    = new JRWS_Tuple($def, $this);
		$this->dictionary['function'] = new JRWS_Function($def, $this);

		//Build the API
		$this->functions  = $this->original['api'];

		foreach ($this->functions as $name => $definition)
		{
			#echo(sprintf("name=%s definition=%s<br>",$name,$definition));
			$this->assign($this->functions[$name]);
			#echo(print_r($this->functions[$name]));
		}
	}
	
	//Import a JDF from URL
	function import($alias, $url)
	{
		if (!isset($this->root->library[$url]))
		{
			$this->root->import($url);
		}
		$this->aliases[$alias] = &$this->root->library[$url];
	}
	
	//Validate a call a particular function with specified input data
	function call($function, $data)
	{
		## TEST ##
		//Bomb if the API specifies no functions at all
		if (count($this->functions) == 0)
		{
			throw new Exception("The JDF API does not contain any functions");
		}
		
		//If no function is specified then assume the first
		if (!$function)
		{
			$names = array_keys($this->functions);
			###echo("functions:<br>");
			###echo(print_r($names, true));
			###echo("<br>");
			$function = $names[0];
		}
		else {
			//Bomb if the API does not have a matching function
			if (!isset($this->functions[$function]))
			{
				throw new Exception("The JDF API does not have a function named $function");
			}
		}
		
		//Validate the request against the matching function definition
		#echo("JDF_Node validating:<br>");
		#echo(sprintf("function=%s<br>",$function));
		#echo(print_r($this->functions[$function]));
		#echo("<br>");
		return $this->validate($data, $this->functions[$function]);
	}
	
	//Validate a data item against a definition
	function validate(&$data, &$def)
	{
		###echo("def in JDF_Node validate()=");
		###echo(print_r($def, true));
		###echo("<br>");
		if (!$def) return true;
		$this->assign($def);
		##echo("validating<br>");
		##echo(print_r($def, true));
		##echo(print_r($data,true));
		##echo("<br>");
		# TESTING: passing $def into validate function
		###$def_class = get_class($def);
		###echo(sprintf("class of def=%s<br>", $def_class));
		###$result = $def->validate($data,$def);
		###echo("testing result from validate method<br>");
		###if ($result == false)
		###{
		###	echo("result of validate method is false<br>");
		###}
		
		return $def->validate($data, $def);
	}
	
	//Given a node in the JDF tree, convert it to a validation object if necessary
	function assign(&$target)
	{
		if (is_object($target))
		{
			return;
		}
		else if (is_array($target))
		{
			$target = JRWS_Factory::generate($target, $this);
			#echo(sprintf("string=%s", $target->dictionary['string']));
			#echo("<br>");
			return;
		}
		else if (is_string($target))
		{
			$parts = explode('.', $target);
			
			$scope = $this;
			
			foreach ($parts as $path)
			{
				if (isset($scope->aliases[$path]))
				{
					$scope = $scope->aliases[$path];
				}
				else if (isset($scope->dictionary[$path]))
				{
					$scope->assign($scope->dictionary[$path]);
					$target = $scope->dictionary[$path];
				}
				else
				{
					throw new Exception("Unable to find alias '$path'");
				}
			}
		}
		else
		{
			throw new Exception("Illegal type specified in JDF_Node::assign");
		}
	}
}

//The root JDF in the validation build-graph is the primary point of contact for data validation
class JDF_Root
{
	var $raw;
	var $library;
	var $primary;
	
	function JDF_Root($url = '')
	{
		$this->raw = array();
		$this->library = array();
		$this->primary = array();
		
		if ($url)
		{
			$this->build_from_url($url);
		}
	}
	
	function build_from_url($url)
	{
		$this->build(JSON::download($url));
	}
	function build_from_file($file)
	{
		$this->build(JSON::load($file));
	}
	function build_from_string($json)
	{
		$this->build(JSON::decode($json));
	}
	function build_from_object($data)
	{
		$this->build($data);
		##echo print_r($this->raw, true);
	}
	function build($data)
	{
		$this->raw = $data;
		$this->library = array();
		$this->primary = new JDF_Node($this, $data);
		#echo("primary: ");
		#echo(print_r($this->primary, true));
		#echo("<br>");
		$this->library['root'] = $this->primary;
	}
	
	//Import a JDF from URL/
	function import($url)
	{
		if (!isset($this->library[$url]))
		{
			$this->library[$url] = new JDF_Node($this, JSON::download($url));
		}
	}
	
	//Dump the JDF as human-friendly plain text
	function dump_text()
	{
		return JSON::text($this->raw);
	}
	
	//Dump the JDF as a JSON string
	function dump_json()
	{
		return JSON::encode($this->raw);
	}
	
	//Dump the JDF as an HTML string
	function dump_html()
	{
		return JSON::html($this->raw);
	}
	
	//Validate a request
	function validate($function, $data)
	{
		## HN Testing
		##echo("validating<br>");
		##$jtest=$this->primary;
		##echo(print_r($jtest));
		##echo("<br>");
		##echo($this->primary->call($function, $data));
		##$test=$this->primary->call($function, $data);
		##echo(sprintf("test=%s<br>",$test));
		###$class_of_function = get_class($function);
		###echo(sprintf("function class=%s<br>",$class_of_function));
		###echo(sprintf("function=%s<br>",$function));
		return $this->primary->call($function, $data);
	}
}

?>
