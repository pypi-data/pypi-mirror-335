import { NotebookPanel } from '@jupyterlab/notebook';

export const checkSyntax = async (notebookPanel: NotebookPanel) => {
    const messages: string[] = []
    const cells = notebookPanel.model?.cells
    if (cells) {
        for (let celli = 0; celli < cells?.length; celli++) {
            const cell = cells.get(celli)
            if (cell.type === 'code') {
                const source = cell.sharedModel.source.split('\n')
                const baseMap = cell.getMetadata("map")
                console.log(source, baseMap)

                if (source.length !== baseMap.length) {
                    messages.push(`Warning <Cell ${celli}>: The code editor and metadata editor have different line numbers. Please review them before proceeding.`)

                    if (source.length > baseMap.length) {
                        while (source.length > baseMap.length) {
                            baseMap.push({ command: [] })
                        }
                    }
                    
                    if (source.length < baseMap.length) {
                        while (source.length < baseMap.length) {
                            source.push('')
                        }
                    }
                }

                source.forEach((line, linei) => {
                    const commandList: string[] = baseMap[linei]['command']
                    if ('AUDIO' in commandList) {
                        if (line[0] !== '#') {
                            messages.push(`Warning <Cell ${celli}, Line ${linei} >:Bad syntax for AUDIO command, line should start with #`)
                        }
                    }
                    else if (commandList.some(command => command.includes('AUDIOALT'))) {
                    }
                })




            }
        }
    }
    messages.push('Syntax Error')
    return { isValid: false, message: messages.join('\n') };
};
