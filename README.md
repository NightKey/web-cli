# Web-CLI
Easy to use Web CLI for python applications.

# Table of content
 - [Usage](#usage)
 - [Settings](#settings)
 - [WebCLIServer](#webcliserver)

# Usage
Import and make a instantiate it. 
```python
settings = Settings(name="Example page")
server = WebCLIServer(settings, backend)

fun backend(user_command: UserCommand) -> None:
    // do stuff here
```

After, start the server with server.start().

```python
server.start()
```

The example provded will result in a webserver opened on 127.0.0.1:8080 (localhost:8080). Opening this page will result in a command line looking webpage that can communicate with the server.

# Settings
 - host: Host's IP.
 - port: Port for the IP address.
 - name: Name of the web server.

## functions

### to_file
 - string_path (str or None): A string path for the settings file.

Creates a config file with the path provided or in the current folder witht he default name. 

### from_file
 - string_path (str or None): A string path for the settings file.

Reads the file provided, and creates a settings class.

# WebCLIServer
 - settings: Settings data to set up the server.
 - backend: A func that can handle UserCommand data class as input, and do something with it, with a return value that's ignored.
 - logger: An smdb_logger logger. It can be None or ignored, so it won't produce output on stdrout.

## functions

### push_data
 - response (str or List[str]): The output for a user command.
 - command (UserCommand or None): The user command to reply to. If None, the last command will be used.

Adds a response for a user command. It can be used to oush data to the web cli, with command being not set, it will result in the data being pushed to the last command in the history.

### start
Starts the server.

### stop
Stops the server.