# Title     : R Logger
# Objective : Adds logging functionality similar to that of in Python
# Created by: bobrock
# Created on: 12/9/18


setup_logger = function(path_prefix, log_name)
{
    options(digits.secs=3)
    suppressWarnings(require(logging))
    basicConfig(level='FINEST')
    addHandler(
        writeToFile,
        file=paste0(path_prefix, strftime(Sys.Date(), '%Y%m%d'), '.log'),
        logger=log_name,
        level='DEBUG')
}

prefix = '. - '

log_info = function(text)
{
    loginfo(msg=paste0(prefix, text), logger=logname)
}

log_debug = function(text)
{
    logdebug(msg=paste0(prefix, text), logger=logname)
}

log_error = function(err)
{
    logerror(paste0(prefix, 'Error occurred: ', err), logger=logname)
}

log_warning = function(war)
{
    logwarn(paste0(prefix, 'Warning encountered: ', war), logger=logname)
}

try_catch = function(success_text, command)
{
    tryCatch(
        {
            command
        }, warning = function(war)
        {
            log_warning(war)
        }, error = function(err)
        {
            log_error(err)
        }, finally = {
            log_info(success_text)
        }
    )
}

