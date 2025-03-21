class ArgocdPhase:
    def get_phase(phase,paas):
        
        if phase in ['prd','ppt','ccp','red']:
            if 'tst' in paas or 'nld7'in paas or 'nld8' in paas:
                argo_phase='tst'
            else: 
                argo_phase='prd' 
        elif phase=='rnd':
            argo_phase='rnd'
        else:
            argo_phase='tst'
        # print(argo_phase)
        return argo_phase