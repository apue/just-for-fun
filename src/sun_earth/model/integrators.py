
class Integrator:
    @staticmethod
    def step(system, dt, method='leapfrog'):
        """
        Advance the system by one time step dt using the specified method.
        """
        if method == 'euler':
            Integrator.euler_step(system, dt)
        elif method == 'leapfrog':
            Integrator.leapfrog_step(system, dt)
        else:
            raise ValueError(f"Unknown integration method: {method}")

    @staticmethod
    def euler_step(system, dt):
        """
        Explicit Euler Method (First Order).
        v(t+dt) = v(t) + a(t) * dt
        x(t+dt) = x(t) + v(t) * dt
        """
        system.compute_forces() # Update a(t) based on x(t)
        
        for body in system.bodies:
            # We must use curr vel for pos update in explicit Euler
            # But we update vel in place, so careful with order if we want strict Euler
            # Standard implementation often does:
            # v += a * dt
            # x += v * dt (This is actually Semi-Implicit Euler / Symplectic Euler)
            
            # Strict Explicit Euler:
            # x_new = x + v * dt
            # v_new = v + a * dt
            
            # Implementing Symplectic Euler (better stability than explicit)
            # v += a * dt
            # x += v * dt
            
            # Wait, user asked for Euler to show it's BAD (drifts). 
            # Explicit Euler is the bad one.
            
            # Save current velocity for position update
            v_curr = body.velocity.copy()
            
            body.velocity += body.acceleration * dt
            body.position += v_curr * dt # Use old velocity
            
            body.history.append(body.position.copy())

    @staticmethod
    def leapfrog_step(system, dt):
        """
        Leapfrog / Velocity Verlet (Second Order, Symplectic).
        Good for energy conservation.
        
        Drift-Kick-Drift or Kick-Drift-Kick form.
        Here using a synchronized form (Velocity Verlet):
        v(t+0.5dt) = v(t) + 0.5 * a(t) * dt
        x(t+dt) = x(t) + v(t+0.5dt) * dt
        Include force update a(t+dt)
        v(t+dt) = v(t+0.5dt) + 0.5 * a(t+dt) * dt
        """
        
        # 1. First half-kick: v += 0.5 * a * dt
        # We need a(t) first.
        # Assuming system.compute_forces() was called before or acceleration is valid from last step.
        # For the very first step, we might need to compute forces manually if not done.
        # But generally, we can assume acceleration is current.
        
        # Note: If this is the START of simulation, caller should ensure compute_forces() is called once.
        # Let's enforce it here just in case? No, that doubles work.
        # We'll assume a(t) is valid.
        
        for body in system.bodies:
            body.velocity += 0.5 * body.acceleration * dt
            
        # 2. Drift: x += v * dt
        for body in system.bodies:
            body.position += body.velocity * dt
            body.history.append(body.position.copy())
            
        # 3. Update forces: a(t+dt)
        system.compute_forces()
        
        # 4. Second half-kick: v += 0.5 * a_new * dt
        for body in system.bodies:
            body.velocity += 0.5 * body.acceleration * dt
