/*
pyodide-mkdocs-theme
Copyleft GNU GPLv3 🄯 2024 Frédéric Zinelli

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.
If not, see <https://www.gnu.org/licenses/>.
*/


import { jsLogger } from 'jsLogger'
import {
  decompressPagesIfNeeded,
  noStorage,
  sleep,
  unEscapeSquaredBrackets,
  withPyodideAsyncLock,
  youAreInTroubles,
} from 'functools'
import { _DUMMY } from 'process_and_gui'   // Enforce dependencies order (if ever a runner is needed)

import { pyodideFeatureRunCode } from '0-generic-python-snippets-pyodide'
import { RuntimeManager } from '1-runtimeManager-runtime-pyodide'





export class RunningProfile {

  static PROFILE = Object.freeze({
    cmd:          'Command',
    btn:          'PyBtn',
    play:         'Play',
    validate:     'Validate',
    validateCorr: 'ValidateCorr',
    testing:      'Testing',
    testingPlay:  'TestingPlay',
    testingValid: 'TestingValidate',
    testingCorr:  'TestingValidateCorr',
    testingCmd:   'TestingCommand',
    zipExport:    'zipExport',
    zipImport:    'zipImport',
  })

  static build(profile){
    return Object.freeze({
      name: profile,
      isTermCmd:  profile.includes(RunningProfile.PROFILE.cmd),
      isPlaying:  profile.includes(RunningProfile.PROFILE.play),
      isChecking: profile.includes(RunningProfile.PROFILE.validate),
      isTesting:  profile.includes(RunningProfile.PROFILE.testing),
    })
  }
}

















export class PyodideSectionsRunner {

  static pyFuncs = {}

  no_undefined = prop =>{
      const getter = v => {
        if(v!==undefined) return v
        throw new Error(`Undefined is not allowed: ${this.constructor.name}.${prop}.`)
      }
      return getter
  }

  //JS_CONFIG_DUMP
  get attemptsLeft()      { return this.data.attempts_left }
  get autoLogAssert()     { return this.data.auto_log_assert }
  get autoRun()           { return this.data.auto_run }
  get corrContent()       { return this.data.corr_content }
  get corrRemsMask()      { return this.data.corr_rems_mask }
  get cutFeedback()       { return this.data.cut_feedback }
  get deactivateStdoutForSecrets(){ return this.data.deactivate_stdout_for_secrets }
  get decreaseAttemptsOnUserCodeFailure(){ return this.data.decrease_attempts_on_user_code_failure }
  get envContent()        { return this.data.env_content }
  get envTermContent()    { return this.data.env_term_content }
  get excluded()          { return this.data.excluded }
  get excludedKws()       { return this.data.excluded_kws }
  get excludedMethods()   { return this.data.excluded_methods }
  get export()            { return this.data.export }
  get hasCheckBtn()       { return this.data.has_check_btn }
  get hasCorrBtn()        { return this.data.has_corr_btn }
  get hasCounter()        { return this.data.has_counter }
  get hasRevealBtn()      { return this.data.has_reveal_btn }
  get isEncrypted()       { return this.data.is_encrypted }
  get isVert()            { return this.data.is_vert }
  get maxIdeLines()       { return this.data.max_ide_lines }
  get minIdeLines()       { return this.data.min_ide_lines }
  get postContent()       { return this.data.post_content }
  get postTermContent()   { return this.data.post_term_content }
  get prefillTerm()       { return this.data.prefill_term }
  get profile()           { return this.data.profile }
  get publicTests()       { return this.data.public_tests }
  get pyName()            { return this.data.py_name }
  get pypiWhite()         { return this.data.pypi_white }
  get pythonLibs()        { return this.data.python_libs }
  get recLimit()          { return this.data.rec_limit }
  get secretTests()       { return this.data.secret_tests }
  get showOnlyAssertionErrorsForSecrets(){ return this.data.show_only_assertion_errors_for_secrets }
  get srcHash()           { return this.data.src_hash }
  get stdKey()            { return this.data.std_key }
  get stdoutCutOff()      { return this.data.stdout_cut_off }
  get twoCols()           { return this.data.two_cols }
  get userContent()       { return this.data.user_content }
  get whiteList()         { return this.data.white_list }
  //JS_CONFIG_DUMP





  constructor(id, callInit=true){
    LOGGER_CONFIG.ACTIVATE && jsLogger('[CheckPoint] - Constructor for', this.constructor.name, id)

    decompressPagesIfNeeded()

    this.id = id
    this.data = this._prepareData(PAGE_IDES_CONFIG[id])
    if(CONFIG._devMode)
      CONFIG.objs[this.id] = this
    else{
      delete PAGE_IDES_CONFIG[id]
    }
    this.getCodeToTest = ()=>""   // If no editor, nothing to test...
    this.running = undefined      // RunningProfile
    this.allowPrint = true
    this.isGuiCompliant = false   // All the GUI makeup has been applied (may not be, right at the beginning, for tabbed contents, typically)

    if(callInit) this._init()
  }


  _prepareData(data){
    data.python_libs = new Set(data.python_libs)
    return data
  }


  _init(){}     // Super calls sink...


  build(){
    // Using setTimeout to be sure the `build` step will be complete (some children classes
    // may have subsequent operations after the super method, aka here, has been called).
    if(this.autoRun){
      setTimeout(async ()=>await this.applyAutoRun())
    }
    this.makeUpYourGui()
  }



  /**Actions to perform when the element becomes "visible" in the page.
   * Here "visible" is "not hidden", CSS-wise (see `=== "tabbed"`, typically).
   * */
  makeUpYourGui(){
    return this.isGuiCompliant = true
  }



  /** Generic call for macros with AUTO_RUN=True (once the runner callback is defined...).
   * */
  async applyAutoRun(){
    await this._defaultAutoRun()
  }

  /**Allow to keep the same implementation for the IDE class, while the intermediate Terminal
   * class has its own logic for autoRun.
   * */
  async _defaultAutoRun(){
    while(!this.runner) await sleep(40)
    await this.runner()
  }


  /**Store code or command in the python runtime.
   * */
  storeUserCodeInPython(varName, code){
    const showOff = JSON.stringify(code.length>50 ? code.slice(0,50)+' ...' : code)
    LOGGER_CONFIG.ACTIVATE && jsLogger('[CheckPoint] - Store ', varName, showOff)

    // The double quotes are all escaped to make sure no multiline string will cause troubles
    const escapedCode = code.replace(/"/g, '\\"')
    pyodide.runPython(`__builtins__.${ varName } = """${ escapedCode }"""`)
  }



  /**Runners without any terminal won't ever give feedback, unless it's a critical error.
   * In that case, a window alert will be used, so that it doesn't go unnoticed.
   * */
  giveFeedback(content, format='error'){
    if(content && format=='error'){
      // Format back any escaped square brackets, because window.alert is not the terminal...
      window.alert( unEscapeSquaredBrackets(content) )
    }
  }



  /**Creates a generic "action runner", handling the overall security logic, catching exceptions
   * that are thrown up to this point and displaying them in a BigFail-fashion-way in the terminal.
   *
   * Contracts:
   *    - @setup takes the `e` (event) argument only and returns a RuntimeManager instance.
   *      The argument may be:
   *        * either an `Event`: then it has no use.
   *        * or the current terminal command (`string`) that just got validated in the console.
   *    - @action takes the runtime argument and returns nothing
   *    - @finallyTeardown takes the runtime argument and returns nothing.
   *
   * About executions:
   *    - @actionName : RunningProfile.PROFILES value to be able to identify what's currently running.
   *    - @setup is always run
   *    - @action is always called, and it is its job to decide if it has to actually run its
   *       logic or not, depending on the `runtime` state.
   *    - @finallyTeardown is always called, and should contain all the operations that HAVE
   *       to be run whatever happened before (success/error). Both are almost guaranteed to
   *       happen, whatever the outcome of the others executions was: the only exception would
   *       be a crash during @setup, that wouldn't return any `runtime` object (this would lead
   *       to a BIG_FAIL error thrown in he JS console).
   * */
  lockedRunnerWithBigFailWarningFactory(
    actionName,       // string, logging purpose + used to identify what's currently running.
    setup,            // async, args: eventOrTermCmdString
    action,           // async, args: runtime
    finallyTeardown,  // async, args: runtime (guaranteed to run)
    sendEventOrCmdToAction = false,   // Useful for drag & drop (IDE zip imports)
  ){
    const loggerName = `[${actionName}]`
    const runningMan = RunningProfile.build(actionName)

    return withPyodideAsyncLock(actionName, async(eventOrCmd)=>{
      if(eventOrCmd && eventOrCmd.preventDefault) eventOrCmd.preventDefault()
      LOGGER_CONFIG.ACTIVATE && jsLogger(loggerName)

      this.running = runningMan
      let runtime
      try{
        runtime = await setup.call(this, eventOrCmd)
        await action.call(this, sendEventOrCmdToAction ? eventOrCmd : runtime)

      }catch(e){
        LOGGER_CONFIG.ACTIVATE && jsLogger("[CheckPoint] - BIG FAIL", actionName)

        // If something didn't get caught, it's very wrong... so give feedback to the user
        // in BIG and RED:
        const stdErr = youAreInTroubles(e)
        this.giveFeedback(stdErr)

        if(runtime){                  // (`runtime` may be undefined if the error was in setup...)
          runtime.gotBigFail = true
          runtime.stdErr     = stdErr
        }
        throw e

      }finally{
        LOGGER_CONFIG.ACTIVATE && jsLogger("[CheckPoint] - finally", actionName)
        if(runtime){
          await finallyTeardown.call(this, runtime)
        }
        this.running = undefined
      }
    })
  }





  /**Build the default configuration runtime to use to run the user's code.
   * */
  setupGlobalConfig(){
    CONFIG.runningId      = this.id
    CONFIG.running        = this.running.name
    CONFIG.termMessage    = ()=>undefined    // sink
    for(const prop of 'get del set keys'.split(' ')){
      const globName = prop+'Storage'
      const method   = `pyodide${ _.capitalize(prop) }Storage`
      globalThis[globName] = this[method].bind(this)    // Legacy behavior
    }
  }

  pyodideGetStorage(key)  { noStorage() }   // sink
  pyodideKeysStorage()    { noStorage() }   // sink
  pyodideSetStorage(k, v) { noStorage() }   // sink
  pyodideDelStorage(key)  { noStorage() }   // sink




  // Sink: Just in case the implementation goes wrong somewhere...
  //       CONFIG.termMessage normally has no effect: see this.setupGlobalConfig.
  termFeedbackFromPyodide(){
    throw new Error("Y'shall never get there, mate...")
  }





  /** 1. Refresh the features defined in pyodide environment, in case the user messed with them
   *     (accidentally or not).
   *  2. Then run the content of the `env` section.
   *
   * @returns: RuntimeManager object.
   * */
  async setupRuntime(srcRuntime=null, section='env'){
    LOGGER_CONFIG.ACTIVATE && jsLogger('[CheckPoint] - setupRuntime PyodideSectionsRunner')

    const runtime = await this._baseSetupRuntime(srcRuntime, section)
    await runtime.runWithCtx(section)
    return runtime
  }


  async _baseSetupRuntime(srcRuntime, section){
    this.setupGlobalConfig()
    const runtime = srcRuntime || new RuntimeManager(this)
    await runtime.runWithCtx({
      section:    section ?? 'env',
      method:     this.refreshPyodideFeatures,
      autoImport: false,    // Nothing to install, with the Pyodide Features!
    })
    return runtime
  }


  refreshPyodideFeatures(){
    ;`
      ioStuff
      version
      localStorageRelays
      copyFromServer
      exclusionsTools
      mermaidDrawer
      refresher
      upDownLoader
    `.trim()
     .split(/\s+/)
     .forEach(pyodideFeatureRunCode)
  }





  /**Takes a user code as argument, and run it in the pyodide environment, using various runtime
   * logics. It mutates the RuntimeManager objects on the way, keeping track of the current state
   * of the executions (error or not, keep running or not, ...).
   *
   * Operations done:
   *    1. Run methods exclusion check (if not needed, the method is called but won't do anything).
   *    2. If the runtime is marked as stopped, stop here.
   *    3. Try to install/import missing packages or python_libs.
   *    4. If the runtime is marked as stopped, stop here.
   *    5. Actually run the given code in Pyodide.
   *
   * @throws: Any JS runtime Error if something went very wrong... (python errors are swallowed
   *          and just printed to the jQuery.terminal)
   * */
  async runPythonCodeWithOptionsIfNoStdErr(code, runtime, testsStep){
    LOGGER_CONFIG.ACTIVATE && jsLogger('[CheckPoint] - Enter generic running function')

    // Do nothing if nothing to do...!
    if(runtime.stopped) return;

    const someCodeToRun = code.trim()
    if(someCodeToRun){

      const ctx = {
        code,
        section: 'code',
        logConfig: {
          code,
          purgeTrace: runtime.purgeStackTrace,
          autoAssertExtraction: runtime.autoLogAssert,
        },
        asyncSecrets: testsStep === CONFIG.section.secrets,
        method: async (ctx)=>{
          if(ctx.asyncSecrets){
            await pyodide.runPythonAsync(ctx.code)
          }else{
            pyodide.runPython(ctx.code)
          }
        },
        isEnvSection: false,
        applyExclusionsIfAny: true,
      }
      // No ast exclusions for validations' code:
      if(testsStep!==CONFIG.section.editor){
        ctx.kwsExclusions = ctx.methodsExclusions = false
      }
      await runtime.runWithCtx(ctx)
    }

    // Potentially give some feedback in the terminal to the user, about what happened:
    this.codeSnippetEndFeedback(runtime, testsStep, code)
  }


  /** Nothing to do by default (specific to IDEs) */
  codeSnippetEndFeedback(runtime, step, code){}




  async teardownRuntime(runtime){
    LOGGER_CONFIG.ACTIVATE && jsLogger("[CheckPoint] - PyodideSectionsRunner teardownRuntime")

    await runtime.runWithCtx('post')
    await this.handleMermaids(runtime)
    await this._baseTeardownRuntime(runtime)
  }

  async _baseTeardownRuntime(runtime){
    LOGGER_CONFIG.ACTIVATE && jsLogger("[CheckPoint] - teardown pyodide cleaner")
    pyodideFeatureRunCode('autoRunCleaner')
    runtime.cleanup()
  }



  async handleMermaids(runtime){
    LOGGER_CONFIG.ACTIVATE && jsLogger("[CheckPoint] - teardown mermaid")

    if(!CONFIG.needMermaid || runtime.stopped){
      return
    }

    if(!globalThis.mermaid){
      this.giveFeedback(
        'Cannot convert to mermaid graph: mermaid is not available.\n'
        +'Please contact the author of the exercice.'
      )
    }
    try{
      await mermaid.run()
      // mermaid.run systematically throws an error, even on valid graphs...
      // Worse: If mermaid.run({suppressErrors:true}) is used, nothing is rendered at all...
      //        (I love JS...)
    }catch(e){}
  }
}
